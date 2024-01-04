from database.biblio.models import Affiliation
from database.biblio.selects import affiliations_publications
from verifiers.base_verifier import BaseVerifier


class CountriesVerifier(BaseVerifier):

    next_verifier = None
    isStrict = True
    succeed = None
    fail = None
    flag = False

    def __init__(self, isStrict, succeed, fail, countries):
        self.countries = countries
        super().__init__(isStrict, succeed, fail)

    # Метод верифікації
    def verify(self, p, verified_pubs, pub_affs):
        # Формування списку країн видання для даної публікації
        p_countries = [a.affiliation.country for a in affiliations_publications().join(Affiliation)
                       if a.affiliation_publication_id in pub_affs]

        # Якщо перевірка строга
        if self.isStrict:
            # Якщо є збіг по країнам видання
            if len(list(set(self.countries) & set(p_countries))) != 0:
                # Відмічення прапору успіху
                self.flag = True
                # Передача запиту базовому обробнику
                super().verify(p, verified_pubs, pub_affs)
        else:
            # Якщо є збіг по країнам видання
            if len(list(set(self.countries) & set(p_countries))) != 0:
                # Відмічення прапору успіху
                self.flag = True
                # Якщо статті ще немає у списку верифікованих, то додати її
                if p not in verified_pubs:
                    verified_pubs.append(p)
            # Передача запиту базовому обробнику
            super().verify(p, verified_pubs, pub_affs)
