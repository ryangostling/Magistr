# External
from PyQt5.QtCore import QObject

# Internal
from parsers.core import CoreParser
from parsers.scholar import ScholarParser
from parsers.scotus import ScopusParser


class Parser(QObject):
    def __init__(self, query, signals, coauthors=True, authors=None, sources=None):
        super().__init__()
        if sources is None:
            sources = ['Scopus', 'CORE', 'Google Scholar']
        self.query = query
        self.signals = signals
        self.flag = True
        self.coauthors = coauthors
        self.authors = authors
        self.sources = sources

    # Запуск парсингу Scopus
    def parse_scopus(self):
        self.parser = ScopusParser(self.query, self.signals.set_max_signal, self.signals.progress_signal,
                                   self.signals.status_signal, self.signals.update_signal, coauthors=self.coauthors)
        self.parser.parse()

        if self.authors is None:
            self.authors = self.parser.query_authors

    # Запуск парсингу CORE
    def parse_core(self):
        if self.flag and len(self.authors) != 0:
            self.parser = CoreParser(self.authors, self.signals.set_max_signal, self.signals.progress_signal,
                                     self.signals.status_signal, self.signals.update_signal)
            self.parser.parse()

    # Запуск парсингу Google Scholar
    def parse_scholar(self):
        try:
            print('here')
            if self.flag and len(self.authors) != 0:
                self.parser = ScholarParser(self.authors, self.signals.set_max_signal, self.signals.progress_signal,
                                            self.signals.status_signal, self.signals.update_signal)
                self.parser.parse()
        except Exception as err:
            print(err)

    def run(self):
        try:
            # Запуск парсерів залежно від переданих параметрів
            if 'Scopus' in self.sources:
                self.parse_scopus()

            if 'CORE' in self.sources:
                self.parse_core()

            if 'Google Scholar' in self.sources:
                self.parse_scholar()

            # Виклик сигналу обробки результатів
            self.signals.results_signal.emit()
        except Exception as err:
            print(err)

    # Переривання парсингу
    def abort(self):
        self.flag = False
        self.parser.abort_parsing()
