from abc import abstractmethod, ABC


class Verifier(ABC):
    # Метод встановлення наступного валідатора в ланцюзі
    @abstractmethod
    def set_next(self, verifier):
        ...

    # Метод верифікації
    @abstractmethod
    def verify(self, pub, verified_pubs, pub_affs):
        ...

    # Метод візуалізації результатів
    @abstractmethod
    def visualize(self):
        ...
