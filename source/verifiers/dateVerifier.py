from verifiers.base_verifier import BaseVerifier


class DateVerifier(BaseVerifier):

    next_verifier = None
    isStrict = True
    flag = False
    succeed = None
    fail = None

    def __init__(self, isStrict, succeed, fail, dateFrom, dateTo):
        self.dateFrom = dateFrom
        self.dateTo = dateTo
        super().__init__(isStrict, succeed, fail)

    # Метод верифікації
    def verify(self, p, verified_pubs, pub_affs):
        # Якщо часовий проміжок валідний
        if self.dateFrom <= self.dateTo:
            # Якщо перевірка строга
            if self.isStrict:
                # Якщо статтю опубліковано в часовому діапазоні
                if self.dateFrom <= p.pub_date <= self.dateTo:
                    # Відмічення прапору успіху
                    self.flag = True
                    # Передача запиту базовому обробнику
                    super().verify(p, verified_pubs, pub_affs)
            else:
                # Якщо статтю опубліковано в часовому діапазоні
                if self.dateFrom <= p.pub_date <= self.dateTo:
                    # Відмічення прапору успіху
                    self.flag = True
                    # Якщо статті ще немає у списку верифікованих, то додати її туди
                    if p not in verified_pubs:
                        verified_pubs.append(p)
                # Передача запиту базовому обробнику
                super().verify(p, verified_pubs, pub_affs)
