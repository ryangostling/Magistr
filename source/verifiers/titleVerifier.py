from fuzzywuzzy import fuzz
from verifiers.base_verifier import BaseVerifier


class TitleVerifier(BaseVerifier):

    next_verifier = None
    isStrict = True
    flag = False
    succeed = None
    fail = None

    def __init__(self, isStrict, succeed, fail, title):
        self.title = title
        super().__init__(isStrict, succeed, fail)

    # Метод верифікації
    def verify(self, p, verified_pubs, pub_affs):
        # Якщо перевірка строга
        if self.isStrict:
            # Якщо існують статті з подібною назвою
            if any(filter(lambda t: fuzz.partial_token_sort_ratio(t.lower(), self.title.lower()) >= 75,
                          p.alternative_titles.split(' | '))):
                # Відмічення прапору успіху
                self.flag = True
                # Передача запиту базовому обробнику
                super().verify(p, verified_pubs, pub_affs)
        else:
            # Якщо існують статті з подібною назвою
            if any(filter(lambda t: fuzz.partial_token_sort_ratio(t.lower(), self.title.lower()) >= 75,
                          p.alternative_titles.split(' | '))):
                # Відмічення прапору успіху
                self.flag = True
                # Якщо статті ще немає у списку верифікованих, то додати її туди
                if p not in verified_pubs:
                    verified_pubs.append(p)
            # Передача запиту базовому обробнику
            super().verify(p, verified_pubs, pub_affs)
