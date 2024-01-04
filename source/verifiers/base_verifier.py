# Internal
from verifiers.verifier import Verifier


class BaseVerifier(Verifier):

    next_verifier = None
    isStrict = True
    flag = False
    succeed = None
    fail = None

    def __init__(self, isStrict, succeed, fail):
        self.isStrict = isStrict
        self.succeed = succeed
        self.fail = fail

    # Встановлення наступного валідатора в черзі
    def set_next(self, verifier):
        self.next_verifier = verifier
        return verifier

    # Метод верифікації
    def verify(self, p, verified_pubs, pub_affs):
        # Якщо є наступний валідатор
        if self.next_verifier:
            # Передача публікації по ланцюгу
            self.next_verifier.verify(p, verified_pubs, pub_affs)
        else:
            # Якщо ланцюг закінчився додати публікацію до валідного списку при строгій валідації
            if self.isStrict:
                verified_pubs.append(p)

    # Візуалізація результатів перевірки
    def visualize(self):
        if self.flag:
            self.succeed()
        else:
            self.fail()
