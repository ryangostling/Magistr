from fuzzywuzzy import fuzz
from verifiers.base_verifier import BaseVerifier


class KeywordsVerifier(BaseVerifier):

    next_verifier = None
    isStrict = True
    succeed = None
    fail = None
    flag = False

    def __init__(self, isStrict, succeed, fail, keywords):
        self.keywords = keywords
        super().__init__(isStrict, succeed, fail)

    # Метод верифікації
    def verify(self, p, verified_pubs, pub_affs):
        # Якщо перевірка строга
        if self.isStrict:
            # Якщо є збіг по ключовим словам
            if self.check_keywords(p) or self.check_title(p) or self.check_abstract(p):
                # Відмічення прапору успіху
                self.flag = True
                # Передача запиту базовому обробнику
                super().verify(p, verified_pubs, pub_affs)
        else:
            # Якщо є збіг по ключовим словам
            if self.check_keywords(p) or self.check_title(p) or self.check_abstract(p):
                # Відмічення прапору успіху
                self.flag = True
                # Якщо статті ще немає у списку верифікованих, то додати її
                if p not in verified_pubs:
                    verified_pubs.append(p)
            # Передача запиту базовому обробнику
            super().verify(p, verified_pubs, pub_affs)

    # Метод пошуку співпадінь по визначеним ключовим словам
    def check_keywords(self, p):
        for i in self.keywords:
            for j in p.keywords:
                if fuzz.ratio(i.lower(), j.lower()) >= 75:
                    return True

        return False

    # Метод пошуку співпадінь по назві статті
    def check_title(self, p):
        title_words = p.title.split('.').strip()
        for i in self.keywords:
            for j in title_words:
                if fuzz.partial_token_sort_ratio(i.lower(), j.lower()) >= 60:
                    return True

        return False

    # Метод пошуку співпадінь по анотації
    def check_abstract(self, p):
        if p.abstract == '':
            return False

        abstract_words = p.abstract.split('.').strip()
        for i in self.keywords:
            for j in abstract_words:
                if fuzz.partial_token_sort_ratio(i.lower(), j.lower()) >= 60:
                    return True

        return False
