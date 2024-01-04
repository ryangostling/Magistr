# External
from deep_translator import GoogleTranslator
from fuzzywuzzy import fuzz
from playhouse.shortcuts import model_to_dict
import re
from scholarly import scholarly
import time

# Internal
from database.biblio.adapters import aff_pub_to_dict, auth_pub_to_dict
from database.biblio.context import db
from database.biblio.models import AffiliationAuthor, AffiliationPublication, Publication, AuthorPublication
from database.biblio.selects import publications, affiliations_publications, authors_publications, affiliations_authors
from extractors.scholar import ScholarExtractor
from parsers.consolidation import tokenize, build_name, clear_garbage


# Створення об'єкту гугл-перекладача
translator = GoogleTranslator(source='auto', target='en')

class ScholarParser:
    def __init__(self, authors, set_max, progress_signal, status_signal, update_signal, frequency=90):
        self.authors = authors

        self.publications = [p for p in publications()]
        self.new_publications = []
        self.affs_pubs = [p for p in affiliations_publications()]
        self.new_affs_pubs = []
        self.auths_pubs = [p for p in authors_publications()]
        self.new_auths_pubs = []

        self.flag = True
        self.setMax = set_max
        self.progressSignal = progress_signal
        self.statusSignal = status_signal
        self.updateSignal = update_signal
        self.frequency = frequency

        self.extractor = ScholarExtractor()

    # Головний метод парсингу
    def parse(self):
        print('[SCHOLAR PARSER] start parsing...')
        try:
            start = time.time()
            print(len(self.authors))
            pages = len(self.authors)
            page = 0
            print(f'found {pages} results')
            self.setMax.emit(pages)
            self.progressSignal.emit(page)

            for author in self.authors:
                if self.flag:
                    self.statusSignal.emit(f'Scholar\nЗавантаження статтей автора {page + 1} з {pages}')
                    affiliations = [a.affiliation for a in
                                    affiliations_authors().where(AffiliationAuthor.author == author)]
                    surname = author.name.split(' ')[0]

                    for affiliation in affiliations:
                        self.author = author
                        self.affiliation = affiliation
                        aff_name = re.sub('“.*?”', '', affiliation.affiliation_name).strip()
                        # Запуск парсингу автора за іменем і афіляцією
                        self.parse_author(surname, author.name, aff_name)

                    self.progressSignal.emit(page + 1)
                    # Періодичне оновлення внутрішньої БД
                    if time.time() - start >= self.frequency:
                        self.save()
                    page += 1
            self.save()
            print('[SCHOLAR PARSER] finish parsing...')
        except Exception as err:
            print(err)

    # Парсинг автора
    def parse_author(self, surname, name, aff_name):
        print('[SCHOLAR PARSER] start author parsing...')
        try:
            # Пошук автора в Google Scholar
            search = scholarly.search_author(f'{surname}, {aff_name}')
            # Для кожного знайденого автора
            for author in search:
                if not self.flag:
                    return

                # Приведення імені з запиту до належного для перевірки вигляду
                requested_tokens = tokenize(surname, name)
                requested_name = build_name(requested_tokens)
                # Приведення знайденого імені до належного для перевірки вигляду
                found_tokens = tokenize(surname, author['name'])
                found_name = build_name(found_tokens)

                # Якщо імена подібні з коефіціентом більш за 93
                if fuzz.ratio(requested_name, found_name) >= 93:
                    # Парсинг публікацій для знайденого автора
                    self.parse_publications(author)
            print('[SCHOLAR PARSER] finish author parsing...')
        except Exception as err:
            print(err)

    # Парсинг публікацій
    def parse_publications(self, scholar_author):
        print('[SCHOLAR PARSER] start publication parsing...')
        try:
            # Завантаження зі Scholar всіх публікацій автора
            pubs = [p for p in scholarly.fill(scholar_author, sections=['publications'])['publications']]
            # Для кожної статті автора зі Scholar
            for scholar_pub in pubs:
                if not self.flag:
                    return

                # Пропуск публікацій без назви
                if 'title' not in scholar_pub['bib'] or scholar_pub['bib']['title'] == '':
                    continue

                # Переклад назви публікації на англійську
                title = translator.translate(scholar_pub['bib']['title'])
                # Очистка назви від сміття
                title = clear_garbage(title)

                # Якщо статті з подібною назвою не існує (Виконується нечітке порівняння за токенами)
                if not any(filter(lambda p: fuzz.partial_token_sort_ratio(p.title.lower(), title.lower()) >= 75,
                                  self.publications)):
                    # Обробка нової публікації
                    self.parse_new_publication(title, scholar_pub, scholar_author)
                else:
                    # Обробка існуючої публікації
                    self.parse_existing_publication(title, scholar_pub, scholar_author)

            print('[SCHOLAR PARSER] finish publication parsing...')
        except Exception as err:
            time.sleep(1)
            print(err)

    # Обробка нової публікації
    def parse_new_publication(self, title, scholar_pub, scholar_author):
        print('[SCHOLAR PARSER] publication doesnt exist')
        # Обробка анотації в разі її наявності в базі Scholar
        if 'abstract' in scholar_pub['bib']:
            abstract = clear_garbage(scholar_pub['bib']['abstract'])
        else:
            abstract = ''

        # Обробка тем автора в разі їх наявності в базі Scholar
        if 'interests' in scholar_author and scholar_author['interests'] is not None:
            print('keywords translating')
            keywords = '; '.join([translator.translate(i)
                                  for i in scholar_author['interests']])
        else:
            keywords = ''

        # Обробка оригінальної назви статті, додавання її до списку альтернативних назв
        orig_title = clear_garbage(scholar_pub['bib']['title'])
        if title.lower() != scholar_pub['bib']['title'].lower():
            alternative_titles = f"{title} | {orig_title}"
        else:
            alternative_titles = orig_title

        # Створення нової публікації та занесення до списків
        pub = self.extractor.create_publication(scholar_pub, title, abstract, keywords, alternative_titles)
        self.new_publications.append(pub)
        self.publications.append(pub)

        # Створення зв'язків видавця і публікації та занесення до списків
        af_p = self.extractor.create_affiliation_publication(self.affiliation, pub)
        self.new_affs_pubs.append(af_p)
        self.affs_pubs.append(af_p)

        # Створення зв'язків автора і публікації та занесення до списків
        au_p = self.extractor.create_author_publication(self.author, pub)
        self.new_auths_pubs.append(au_p)
        self.auths_pubs.append(au_p)

    # Обробка існуючої публікації
    def parse_existing_publication(self, title, scholar_pub, scholar_author):
        print('[SCHOLAR PARSER] publication exists')
        pub = list(filter(lambda p: fuzz.partial_token_sort_ratio(p.title.lower(), title.lower()) >= 75,
                          self.publications))[0]

        # Обробка оригінальної назви статті, додавання її до списку альтернативних назв
        orig_title = clear_garbage(scholar_pub['bib']['title'])
        if orig_title not in pub.alternative_titles.split(' | '):
            alternative_titles = pub.alternative_titles.split(' | ')
            alternative_titles.append(orig_title)
            pub.alternative_titles = ' | '.join(alternative_titles)

        # Додавання ідентифікатору статті в Google Scholar
        if 'author_pub_id' in scholar_pub:
            pub.scholar_id = scholar_pub['author_pub_id']

        # Збереження змін
        pub.save()

        # Створення зв'язків видавця і публікації та занесення до списків в разі їх відсутності
        if not any(filter(lambda ap: ap.affiliation == self.affiliation and
                                     ap.publication == pub, self.affs_pubs)):
            af_p = self.extractor.create_affiliation_publication(self.affiliation, pub)
            self.new_affs_pubs.append(af_p)
            self.affs_pubs.append(af_p)

        # Створення зв'язків автора і публікації та занесення до списків в разі їх відсутності
        if not any(filter(lambda ap: ap.author == self.author and
                                     ap.publication == pub, self.auths_pubs)):
            au_p = self.extractor.create_author_publication(self.author, pub)
            self.new_auths_pubs.append(au_p)
            self.auths_pubs.append(au_p)

    # Переривання парсингу
    def abort_parsing(self):
        self.flag = False

    # Збереження даних в БД
    def save(self):
        print('[SCHOLAR PARSER] start saving')
        try:
            with db.atomic():
                flag = False
                if len(self.new_publications) != 0:
                    print('[SCHOLAR PARSER] saving pubs')
                    flag = True
                    pubs = [model_to_dict(p) for p in self.new_publications]
                    Publication.insert_many(pubs).execute()
                    self.new_publications = []

                if len(self.new_auths_pubs) != 0:
                    print('[SCHOLAR PARSER] saving auths_pubs')
                    flag = True
                    pubs = [auth_pub_to_dict(p) for p in self.new_auths_pubs]
                    AuthorPublication.insert_many(pubs).execute()
                    self.new_auths_pubs = []

                if len(self.new_affs_pubs) != 0:
                    print('[SCHOLAR PARSER] saving affs_pubs')
                    flag = True
                    pubs = [aff_pub_to_dict(p) for p in self.new_affs_pubs]
                    AffiliationPublication.insert_many(pubs).execute()
                    self.new_affs_pubs = []
            if flag:
                self.updateSignal.emit()
            print('[SCHOLAR PARSER] finish saving')
        except Exception as err:
            print(err)
