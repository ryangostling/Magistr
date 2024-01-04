# External
import json
from fuzzywuzzy import fuzz
from playhouse.shortcuts import model_to_dict
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval, AuthorRetrieval, AffiliationRetrieval
import pybliometrics.scopus.utils as utils
import time

# Internal
from database.biblio.adapters import aff_pub_to_dict, auth_pub_to_dict, aff_auth_to_dict, auth_sub_to_dict, pub_sub_to_dict
from database.biblio.context import db
from database.biblio.models import AffiliationAuthor, AffiliationPublication, Publication, AuthorPublication, Author, \
    Affiliation, Subject, AuthorSubject, PublicationSubject
from database.biblio.selects import publications, affiliations_publications, authors_publications, affiliations_authors, \
    authors, subjects, affiliations, authors_subjects, publications_subjects
from extractors.scotus import ScopusExtractor
from parsers.consolidation import clear_garbage


# Ініціалізація ключів Scopus
if utils.config['Authentication']['APIKey'] is None or len(utils.config['Authentication']['APIKey']) == 0:
    with open('config.json') as cfg:
        json_data = json.load(cfg)
        api_key = json_data['api_keys']['Scopus']['key']
        token = json_data['api_keys']['Scopus']['token']
        utils.create_config([api_key], token)


class ScopusParser:
    def __init__(self, query, set_max, progress_signal, status_signal, update_signal, frequency=90, coauthors=True):
        self.flag = True
        self.query = query
        self.setMax = set_max
        self.progressSignal = progress_signal
        self.statusSignal = status_signal
        self.updateSignal = update_signal
        self.frequency = frequency
        self.coauthors = coauthors

        self.extractor = ScopusExtractor()
        self.init_db()
        self.query_authors = []

    # Завантаження даних з локальної БД
    def init_db(self):
        self.subjects = [s for s in subjects()]
        self.new_subjects = []
        self.authors = [a for a in authors()]
        self.new_authors = []
        self.affiliations = [a for a in affiliations()]
        self.new_affiliations = []
        self.publications = [p for p in publications()]
        self.new_publications = []
        self.affiliations_publications = [ap for ap in affiliations_publications()]
        self.new_affiliations_publications = []
        self.authors_publications = [ap for ap in authors_publications()]
        self.new_authors_publications= []
        self.authors_subjects = [ass for ass in authors_subjects()]
        self.new_authors_subjects = []
        self.publications_subjects = [ps for ps in publications_subjects()]
        self.new_publications_subjects = []
        self.affiliations_authors = [aa for aa in affiliations_authors()]
        self.new_affiliations_authors = []

    # Головний метод парсингу
    def parse(self):
        print('[SCOPUS PARSER] start advanced parsing...')
        try:
            start = time.time()
            self.statusSignal.emit(f'Пошук даних...')

            # Пошук публікацій за запитом
            search = ScopusSearch(self.query, download=False)

            # В разі, якщо публікації знайдено
            if search.results is not None:
                pages = search.get_results_size()
                page = 0
                print(f'found {pages} results')
                self.setMax.emit(pages)
                search = ScopusSearch(self.query)
                for r in search.results:
                    self.statusSignal.emit(f'Scopus\nЗавантаження статті {page} з {pages}')
                    if self.flag:
                        # Отримання ідентифікатору публікації в Scopus
                        sid = r.eid.split('-')[-1]
                        # Обробка публікації за ідентифікатором
                        pub = self.parse_publication(sid)
                        self.load_authors(pub)

                        self.progressSignal.emit(page + 1)
                        # Оновлення внутрішньої БД за частотою
                        if time.time() - start > self.frequency:
                            self.save()
                            start = time.time()
                        page += 1
                    else:
                        self.save()
                        break
                print('[SCOPUS PARSER] finish advanced parsing...')
                self.save()
        except Exception as err:
            print(err)

    def load_authors(self, pub):
        if pub is not None:
            if self.coauthors:
                authors = [ap.author for ap in self.authors_publications
                           if ap.publication == pub and ap.author not in self.query_authors]
                self.query_authors.extend(authors)
            else:
                surname = self.query[self.query.find("(")+1:self.query.find(")")].split(' ')[0]
                authors = [ap.author for ap in self.authors_publications
                           if ap.publication == pub and ap.author not in self.query_authors
                           and fuzz.ratio(ap.author.surname, surname) >= 95]
                self.query_authors.extend(authors)

    # Обробка публікації
    def parse_publication(self, sid):
        print('[SCOPUS PARSER] start publication parsing...')
        # Якщо публікація відсутня в БД
        if not any(filter(lambda p: p.scopus_id == str(sid).lstrip('0'), self.publications)):
            # Зантаження публікації за ID зі Scopus
            scopus_pub = AbstractRetrieval(sid, view='FULL')

            if len(scopus_pub.authors) > 12:
                return None

            # Обробка анотації, очистка від сміття
            abstract = ''
            if scopus_pub.abstract is not None:
                abstract = clear_garbage(scopus_pub.abstract)
            elif scopus_pub.description is not None:
                abstract = clear_garbage(scopus_pub.description)

            # Обробка визначених ключових слів
            if scopus_pub.authkeywords is None or len(scopus_pub.authkeywords) == 0:
                keywords = ''
            else:
                keywords = '; '.join(scopus_pub.authkeywords)

            # Створення об'єкту публікації
            pub = self.extractor.create_publication(scopus_pub, abstract, keywords)
            # Занесення публікації у списки
            self.publications.append(pub)
            self.new_publications.append(pub)

            # Обробка авторів публікації
            if scopus_pub.authors is not None:
                self.parse_publication_authors(pub, scopus_pub.authors)

            # Обробка видавців публікації
            if scopus_pub.affiliation is not None:
                self.parse_publication_affiliations(pub, scopus_pub.affiliation)

            # Обробка тем публікації
            if scopus_pub.subject_areas is not None:
                self.parse_publication_subjects(pub, scopus_pub.subject_areas)

            return pub
        else:
            # Інакше пошук публікації в БД
            pub = list(filter(lambda p: p.scopus_id == str(sid), self.publications))[0]

        print('[SCOPUS PARSER] finish publication parsing...')
        return pub

    # Обробка авторів публікації
    def parse_publication_authors(self, pub, authors):
        print('[SCOPUS PARSER] start publication authors parsing...')
        for a in authors:
            # Виклик обробника автора за ідентифікатором
            auth = self.get_author(a.auid)
            # Якщо не існує зв'язку між автором і публікацією
            if not any(filter(lambda ap: ap.author == auth and ap.publication == pub, self.authors_publications)):
                # Створюємо зв'язок та вносимо у списки
                ap = self.extractor.create_author_publication(auth, pub)
                self.authors_publications.append(ap)
                self.new_authors_publications.append(ap)
        print('[SCOPUS PARSER] finish publication authors parsing...')

    # Обробка видавців публікації
    def parse_publication_affiliations(self, pub, affiliations):
        print('[SCOPUS PARSER] start publication affiliations parsing...')
        for a in affiliations:
            # Виклик обробника організації за ідентифікатором
            aff = self.get_affiliation(a.id)
            # Якщо не існує зв'язку між видавцем і публікацією
            if not any(filter(lambda ap: ap.affiliation == a and ap.publication == pub, self.affiliations_publications)):
                # Створюємо зв'язок та вносимо у списки
                a_p = self.extractor.create_affiliation_publication(aff, pub)
                self.affiliations_publications.append(a_p)
                self.new_affiliations_publications.append(a_p)
        print('[SCOPUS PARSER] finish publication affiliations parsing...')

    # Обробка тем публікації
    def parse_publication_subjects(self, pub, subject_areas):
        print('[SCOPUS PARSER] start publication subjects parsing...')
        # Виклик обробника списку тем
        subs = self.parse_subjects(subject_areas)
        for s in subs:
            # Якщо не існує зв'язку між темою і публікацією
            if not any(filter(lambda ps: ps.publication == pub and ps.subject == s, self.publications_subjects)):
                # Створюємо зв'язок та вносимо у списки
                p_s = self.extractor.create_publication_subject(pub, s)
                self.publications_subjects.append(p_s)
                self.new_publications_subjects.append(p_s)
        print('[SCOPUS PARSER] finish publication subjects parsing...')

    # Метод парсингу автора
    def get_author(self, sid):
        print('[SCOPUS PARSER] start author parsing...')
        try:
            # Якщо не знайдено автора за ідентифікатором Scopus в БД
            if not any(filter(lambda a: a.scopus_id == str(sid), self.authors)):
                # Завантаження даних про автора зі Scopus
                scopus_auth = AuthorRetrieval(sid)
                # Створення об'єкту автора та занесення у списки
                author = self.extractor.create_author(scopus_auth)
                self.authors.append(author)
                self.new_authors.append(author)

                # Обробка афільованих організацій автора
                if scopus_auth.affiliation_current is not None:
                    self.parse_author_affiliations(author, scopus_auth.affiliation_current)

                # Обробка вказаних у Scopus тем автора
                if scopus_auth.subject_areas is not None:
                    self.parse_author_subjects(author, scopus_auth.subject_areas)
            else:
                # Інакще пошук запису про автора в БД
                author = list(filter(lambda a: a.scopus_id == str(sid), self.authors))[0]

            print('[SCOPUS PARSER] finish author parsing...')
            return author
        except Exception as err:
            print(err)
            return None

    # Обробка афіляцій автора
    def parse_author_affiliations(self, author, affiliations):
        print('[SCOPUS PARSER] start author affiliations parsing...')
        for a in affiliations:
            # Виклик обробника організацій
            aff = self.get_affiliation(a.id)
            # Якщо не існує зв'язку між автором і організацією
            if not any(filter(lambda aa: aa.affiliation == a and aa.author == author, self.affiliations_authors)):
                # Створюємо зв'язок та вносимо у списки
                a_a = self.extractor.create_affiliation_author(aff, author)
                self.affiliations_authors.append(a_a)
                self.new_affiliations_authors.append(a_a)
        print('[SCOPUS PARSER] finish author affiliations parsing...')

    # Обробка інтересів автора
    def parse_author_subjects(self, author, subject_areas):
        print('[SCOPUS PARSER] start author subjects parsing...')
        # Виклик обробника списку тем
        subs = self.parse_subjects(subject_areas)
        for s in subs:
            # Якщо не існує зв'язку між автором і темою
            if not any(filter(lambda ass: ass.author == author and ass.subject == s, self.authors_subjects)):
                # Створюємо зв'язок та вносимо у списки
                a_s = self.extractor.create_author_subject(author, s)
                self.authors_subjects.append(a_s)
                self.new_authors_subjects.append(a_s)
        print('[SCOPUS PARSER] finish author subjects parsing...')

    # Парсинг організацій
    def get_affiliation(self, sid):
        print('[SCOPUS PARSER] start affiliation parsing...')
        try:
            # Якщо не знайдено організацію в БД
            if not any(filter(lambda a: a.scopus_id == str(sid), self.affiliations)):
                # Завантаження даних про організацію зі Scopus
                scopus_aff = AffiliationRetrieval(sid)
                # Створення об'єкту організації та занесення у списки
                aff = self.extractor.create_affiliation(scopus_aff)
                self.affiliations.append(aff)
                self.new_affiliations.append(aff)
            else:
                # Інакше пошук запису організації в БД
                aff = list(filter(lambda a: a.scopus_id == str(sid), self.affiliations))[0]
            print('[SCOPUS PARSER] finish affiliation parsing...')
            return aff
        except Exception as err:
            print(err)
            return None

    # Обробка списку тем
    def parse_subjects(self, subject_areas):
        print('[SCOPUS PARSER] start subjects parsing...')
        subs = []
        for subject in subject_areas:
            # Якщо тему з відповідною назвою не знайдено в БД
            if not any(filter(lambda s: s.full_title == subject.area, self.subjects)):
                # Створення об'єкту теми та занесення у списки
                sub = self.extractor.create_subject(subject)
                self.subjects.append(sub)
                self.new_subjects.append(sub)
            else:
                # Інакше пошук теми в БД
                sub = list(filter(lambda s: s.full_title == subject.area, self.subjects))[0]
            subs.append(sub)
        print('[SCOPUS PARSER] finish subjects parsing...')
        return subs

    # Збереження накопичених даних в БД
    def save(self):
        print('[SCOPUS PARSER] start saving')
        try:
            with db.atomic():
                if len(self.new_publications) != 0:
                    print('[SCOPUS PARSER] saving publications')
                    pubs = [model_to_dict(p) for p in self.new_publications]
                    Publication.insert_many(pubs).execute()
                    self.new_publications = []

                if len(self.new_authors) != 0:
                    print('[SCOPUS PARSER] saving authors')
                    auths = [model_to_dict(a) for a in self.new_authors]
                    Author.insert_many(auths).execute()
                    self.new_authors = []

                if len(self.new_affiliations) != 0:
                    print('[SCOPUS PARSER] saving affiliations')
                    affs = [model_to_dict(a) for a in self.new_affiliations]
                    Affiliation.insert_many(affs).execute()
                    self.new_affiliations = []

                if len(self.new_subjects) != 0:
                    print('[SCOPUS PARSER] saving subjects')
                    subs = [model_to_dict(s) for s in self.new_subjects]
                    Subject.insert_many(subs).execute()
                    self.new_subjects = []

                if len(self.new_affiliations_publications) != 0:
                    print('[SCOPUS PARSER] saving affiliations_publications')
                    pubs = [aff_pub_to_dict(p) for p in self.new_affiliations_publications]
                    AffiliationPublication.insert_many(pubs).execute()
                    self.new_affiliations_publications = []

                if len(self.new_authors_publications) != 0:
                    print('[SCOPUS PARSER] saving authors_publications')
                    pubs = [auth_pub_to_dict(p) for p in self.new_authors_publications]
                    AuthorPublication.insert_many(pubs).execute()
                    self.new_authors_publications = []

                if len(self.new_affiliations_authors) != 0:
                    print('[SCOPUS PARSER] saving affiliations_authors')
                    affs_auths = [aff_auth_to_dict(aa) for aa in self.new_affiliations_authors]
                    AffiliationAuthor.insert_many(affs_auths).execute()
                    self.new_affiliations_authors = []

                if len(self.new_authors_subjects) != 0:
                    print('[SCOPUS PARSER] saving authors_subjects')
                    auths_subs = [auth_sub_to_dict(ass) for ass in self.new_authors_subjects]
                    AuthorSubject.insert_many(auths_subs).execute()
                    self.new_authors_subjects = []

                if len(self.new_publications_subjects) != 0:
                    print('[SCOPUS PARSER] saving publications_subjects')
                    pubs_subs = [pub_sub_to_dict(ps) for ps in self.new_publications_subjects]
                    PublicationSubject.insert_many(pubs_subs).execute()
                    self.new_publications_subjects = []

            self.updateSignal.emit()
            print('[SCOPUS PARSER] finish saving')
        except Exception as err:
            print(err)

    # Переривання парсингу
    def abort_parsing(self):
        self.flag = False
