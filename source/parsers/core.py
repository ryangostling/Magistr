# External
from deep_translator import GoogleTranslator
from fuzzywuzzy import fuzz
import json
from playhouse.shortcuts import model_to_dict
import re
import requests
import time

# Internal
from database.biblio.adapters import aff_pub_to_dict, auth_pub_to_dict
from database.biblio.context import db
from database.biblio.models import AffiliationAuthor, AffiliationPublication, Publication, AuthorPublication
from database.biblio.selects import publications, affiliations_publications, authors_publications, affiliations_authors
from extractors.core import CoreExtractor
from misc.exceptions import *
from parsers.consolidation import tokenize, build_name, clear_garbage

# Створення об'єкту гугл-перекладача
translator = GoogleTranslator(source='auto', target='en')


# Ініціалізація ключа в CORE
with open('config.json') as cfg:
    json_data = json.load(cfg)
    api_key = json_data['api_keys']['CORE']


class CoreParser:
    def __init__(self, authors, set_max, progress_signal, status_signal, update_signal, frequency=90):
        self.base = r'https://core.ac.uk:443/api-v2/articles/search/'
        self.authors = authors
        self.api_key = api_key

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

        self.extractor = CoreExtractor()

    # Приведення запиту до вигляду, прийнятого в CORE
    def build_query(self, author, publisher):
        return f'{self.base}authors:\"{author}\" AND publisher:\"{publisher}\"'

    # Метод для відправки GET-запитів у CORE
    def request_api(self, query, params):
        params['apiKey'] = self.api_key
        for request_try in range(3):
            # Відправка запиту
            response = requests.get(query, params, timeout=60)
            if response.status_code == 200:
                # В разі успіху завантаження json-даних
                return response.json()
            time.sleep(5)

        # Обробка відповідей в разі виникнення помилки
        if response.status_code == 400:
            print('[CORE PARSER: request_api] Invalid identifier supplied')
            raise BadRequest
        elif response.status_code == 401:
            print('[CORE PARSER: request_api] Invalid or no API key provided')
            raise Unauthorized
        elif response.status_code == 403:
            print('[CORE PARSER: request_api] Too many queries in request body')
            raise Forbidden
        elif response.status_code == 429:
            print('[CORE PARSER: request_api] Too many requests in given amount of time')
            raise TooManyRequests
        elif response.status_code == 503:
            print('[CORE PARSER: request_api] Could not run the deduplication service at this time; '
                          'please try again later')
            raise ServiceUnavailable

        print('[CORE PARSER: request_api] Got unrecognized response code')
        raise HTTPException

    # Головний метод парсингу
    def parse(self):
        print('[CORE PARSER] start parsing...')
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
                    self.statusSignal.emit(f'CORE\nЗавантаження статтей автора {page} з {pages}')
                    affiliations = [a.affiliation for a in
                                    affiliations_authors().where(AffiliationAuthor.author == author)]
                    surname = author.name.split(' ')[0]

                    for affiliation in affiliations:
                        self.author = author
                        self.affiliation = affiliation
                        aff_name = re.sub('“.*?”', '', affiliation.affiliation_name).strip()
                        # Запуск парсингу автора за іменем і афіляцією
                        self.parse_query(surname, author.name, aff_name)

                    self.progressSignal.emit(page + 1)
                    if time.time() - start >= self.frequency:
                        self.save()
                    page += 1
            self.save()
            print('[CORE PARSER] finish parsing...')
        except Exception as err:
            print(err)

    # Метод парсингу запиту
    def parse_query(self, surname, name, aff_name):
        print('[CORE PARSER] start query parsing...')
        try:
            # Формування запиту в CORE-вигляді
            query = self.build_query(surname, aff_name)
            hits = 0
            try:
                # Відправка GET-запиту CORE API
                hits = self.request_api(query, {})['totalHits']
            except Exception as err:
                print(err)
            print(f'{hits} found at all')
            # Якщо існують дані за запитом
            if hits != 0:
                # Розділення даних на сторінки
                page_size = 100 if hits >= 100 else hits
                pages = int(hits / page_size) + 1

                # Для кожної сторінки
                for page in range(pages):
                    # Повтор запиту із завантаженням даних
                    response = self.request_api(query, {'page': page + 1, 'pageSize': page_size, 'metadata': 'true',
                                                        'fulltext': 'false', 'citations': 'true', 'similar': 'false',
                                                        'duplicate': 'false', 'urls': 'true',
                                                        'faithfulMetadata': 'false'})
                    if response['data'] is not None:
                        for record in response['data']:
                            author = self.parse_authors(record['authors'], surname, name)
                            affiliation = self.parse_affiliation(record['publisher'])
                            if author is not None and affiliation is not None:
                                self.author = author
                                self.affiliation = affiliation
                                # Обробка публікації
                                self.parse_publication(record)

            print('[CORE PARSER] finish query parsing...')
        except Exception as err:
            print(err)

    # Парсинг публікації
    def parse_publication(self, core_pub):
        print('[CORE PARSER] start publication parsing...')
        try:
            # Переклад назви публікації на англійську
            title = translator.translate(core_pub['title'])
            # Очистка назви від сміття
            title = clear_garbage(title)

            # Якщо статті з подібною назвою не існує (Виконується нечітке порівняння за токенами)
            if not any(filter(lambda p: fuzz.partial_token_sort_ratio(p.title.lower(), title.lower()) >= 75,
                              self.publications)):
                # Обробка нової публікації
                self.parse_new_publication(title, core_pub)
            else:
                # Обробка існуючої публікації
                self.parse_existing_publication(title, core_pub)

            print('[CORE PARSER] finish publication parsing...')
        except Exception as err:
            print(err)

    # Обробка нової публікації
    def parse_new_publication(self, title, core_pub):
        print('[CORE PARSER] publication doesnt exist')

        # Обробка анотації в разі її наявності в базі CORE
        if core_pub['description'] is not None:
            abstract = clear_garbage(core_pub['description'])
        else:
            abstract = ''

        # Обробка тем в разі їх наявності в базі CORE
        if len(core_pub['topics']) != 0:
            print('keywords translating')
            keywords = '; '.join([translator.translate(i)
                                  for i in core_pub['topics']])
        else:
            keywords = ''

        # Обробка оригінальної назви статті, додавання її до списку альтернативних назв
        orig_title = clear_garbage(core_pub['title'])
        if title.lower() != orig_title.lower():
            alternative_titles = f"{title} | {orig_title}"
        else:
            alternative_titles = orig_title

        # Створення нової публікації та занесення до списків
        pub = self.extractor.create_publication(core_pub, title, abstract, keywords, alternative_titles)
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
    def parse_existing_publication(self, title, core_pub):
        print('[CORE PARSER] publication exists')
        pub = list(filter(lambda p: fuzz.partial_token_sort_ratio(p.title.lower(), title.lower()) >= 75,
                          self.publications))[0]

        # Обробка оригінальної назви статті, додавання її до списку альтернативних назв
        orig_title = clear_garbage(core_pub['title'])
        if orig_title not in pub.alternative_titles.split(' | '):
            alternative_titles = pub.alternative_titles.split(' | ')
            alternative_titles.append(orig_title)
            pub.alternative_titles = ' | '.join(alternative_titles)

        # Додавання ідентифікатору статті в CORE
        pub.core_id = core_pub['id']

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

    # Парсинг авторів
    def parse_authors(self, authors, surname, name):
        print('[CORE PARSER] start author parsing...')
        for a in authors:
            # Приведення імені з запиту до належного для перевірки вигляду
            requested_tokens = tokenize(surname, name)
            requested_name = build_name(requested_tokens)
            # Приведення знайденого імені до належного для перевірки вигляду
            found_tokens = tokenize(surname, a)
            found_name = build_name(found_tokens)
            # Якщо імена подібні з коефіціентом більш за 93
            if fuzz.ratio(requested_name, found_name) >= 93:
                print('[CORE PARSER] finish author parsing...')
                return self.author
        print('[CORE PARSER] finish author parsing with None')
        return None

    # Парсинг організацій
    def parse_affiliation(self, affiliation):
        print('[CORE PARSER] start affiliation parsing...')
        if fuzz.ratio(affiliation.lower(), self.affiliation.affiliation_name.lower()) >= 95:
            print('[CORE PARSER] finish affiliation parsing...')
            return self.affiliation
        else:
            print('[CORE PARSER] finish affiliation parsing with None')
            return None

    # Переривання парсингу
    def abort_parsing(self):
        self.flag = False

    # Збереження даних в БД
    def save(self):
        print('[CORE PARSER] start saving')
        try:
            with db.atomic():
                flag = False
                if len(self.new_publications) != 0:
                    print('[CORE PARSER] saving pubs')
                    flag = True
                    pubs = [model_to_dict(p) for p in self.new_publications]
                    Publication.insert_many(pubs).execute()
                    self.new_publications = []

                if len(self.new_auths_pubs) != 0:
                    print('[CORE PARSER] saving auths_pubs')
                    flag = True
                    pubs = [auth_pub_to_dict(p) for p in self.new_auths_pubs]
                    AuthorPublication.insert_many(pubs).execute()
                    self.new_auths_pubs = []

                if len(self.new_affs_pubs) != 0:
                    print('[CORE PARSER] saving affs_pubs')
                    flag = True
                    pubs = [aff_pub_to_dict(p) for p in self.new_affs_pubs]
                    AffiliationPublication.insert_many(pubs).execute()
                    self.new_affs_pubs = []
            if flag:
                self.updateSignal.emit()
            print('[CORE PARSER] finish saving')
        except Exception as err:
            print(err)
