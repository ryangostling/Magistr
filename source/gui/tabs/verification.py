# External
from threading import Lock
import pandas as pd
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QCheckBox, QTableView, QHeaderView, QComboBox, QDateEdit, \
    QProgressBar, QMessageBox

# Internal
from database.biblio.models import Affiliation, Subject, AffiliationAuthor, Author, AuthorPublication, Publication, \
    AffiliationPublication
from database.biblio.queries import get_authors_by_pub_id, get_affiliations_by_pub_id, get_subjects_by_publication_id, \
    get_sources, get_citations_count
from database.biblio.selects import affiliations, subjects, authors, publications, affiliations_publications
from gui.misc.checkedComboBox import CheckedComboBox
from gui.misc.messageBox import show_message
from gui.misc.signalsWrapper import SignalsWrapper
from gui.misc.tableModel import TableModel
from gui.misc.updater import Updater
from misc.filters import filter_publications_by_sources
from parsers.consolidation import tokenize, build_name
from parsers.parser import Parser
from verifiers.citiesVerifier import CitiesVerifier
from verifiers.countriesVerifier import CountriesVerifier
from verifiers.dateVerifier import DateVerifier
from verifiers.keywordsVerifier import KeywordsVerifier
from verifiers.publishersVerifier import PublishersVerifier
from verifiers.titleVerifier import TitleVerifier
from verifiers.topicsVerifier import TopicsVerifier

redrawLock = Lock()
updateLock = Lock()

class VerifierTab:
    # region SETUP

    def __init__(self, page, update, switch):
        self.page = page

        self.update = update
        self.switch = switch
        self.parser = None
        self.parseThread = None
        self.updateThread = None
        self.updater = None

        self.setup_ui()
        self.setup_events()

        self.hide()
        self.clear()
        self.init_ui()
        self.authorCB.setCurrentIndex(-1)
        self.affCB.setCurrentIndex(-1)
        self.countryCCB.clearSelection()
        self.publisherCCB.clearSelection()
        self.topicsCCB.clearSelection()

    def setup_ui(self):
        self.intValidator = QIntValidator()

        self.affL = QLabel(self.page)
        self.affL.setText('Організація')
        self.affCB = QComboBox(self.page)
        self.authorL = QLabel(self.page)
        self.authorL.setText('Автор')
        self.authorCB = QComboBox(self.page)
        self.titleL = QLabel(self.page)
        self.titleL.setText('Назва статті')
        self.titleTB = QLineEdit(self.page)
        self.titleSuccessI = QLabel(self.page)
        self.titleSuccessI.setPixmap(QtGui.QPixmap(r'resources\success.png'))
        self.titleSuccessI.setAlignment(Qt.AlignCenter)
        self.titleFailureI = QLabel(self.page)
        self.titleFailureI.setPixmap(QtGui.QPixmap(r'resources\failure.png'))
        self.titleFailureI.setAlignment(Qt.AlignCenter)
        self.hirshL = QLabel(self.page)
        self.hirshL.setText('Індекс Хірша')
        self.hirshTB = QLineEdit(self.page)
        self.hirshTB.setValidator(self.intValidator)
        self.hirshSuccessI = QLabel(self.page)
        self.hirshSuccessI.setPixmap(QtGui.QPixmap(r'resources\success.png'))
        self.hirshSuccessI.setAlignment(Qt.AlignCenter)
        self.hirshFailureI = QLabel(self.page)
        self.hirshFailureI.setPixmap(QtGui.QPixmap(r'resources\failure.png'))
        self.hirshFailureI.setAlignment(Qt.AlignCenter)
        self.citL = QLabel(self.page)
        self.citL.setText('К-сть цитувань')
        self.citTB = QLineEdit(self.page)
        self.citTB.setValidator(self.intValidator)
        self.citSuccessI = QLabel(self.page)
        self.citSuccessI.setPixmap(QtGui.QPixmap(r'resources\success.png'))
        self.citSuccessI.setAlignment(Qt.AlignCenter)
        self.citFailureI = QLabel(self.page)
        self.citFailureI.setPixmap(QtGui.QPixmap(r'resources\failure.png'))
        self.citFailureI.setAlignment(Qt.AlignCenter)
        self.citTB.setValidator(self.intValidator)
        self.publisherL = QLabel(self.page)
        self.publisherL.setText('Видавець')
        self.publisherCCB = CheckedComboBox(self.page)
        self.publisherSuccessI = QLabel(self.page)
        self.publisherSuccessI.setPixmap(QtGui.QPixmap(r'resources\success.png'))
        self.publisherSuccessI.setAlignment(Qt.AlignCenter)
        self.publisherFailureI = QLabel(self.page)
        self.publisherFailureI.setPixmap(QtGui.QPixmap(r'resources\failure.png'))
        self.publisherFailureI.setAlignment(Qt.AlignCenter)
        self.cityL = QLabel(self.page)
        self.cityL.setText('Місто')
        self.cityCCB = CheckedComboBox(self.page)
        self.citySuccessI = QLabel(self.page)
        self.citySuccessI.setPixmap(QtGui.QPixmap(r'resources\success.png'))
        self.citySuccessI.setAlignment(Qt.AlignCenter)
        self.cityFailureI = QLabel(self.page)
        self.cityFailureI.setPixmap(QtGui.QPixmap(r'resources\failure.png'))
        self.cityFailureI.setAlignment(Qt.AlignCenter)
        self.countryL = QLabel(self.page)
        self.countryL.setText('Країна')
        self.countryCCB = CheckedComboBox(self.page)
        self.countrySuccessI = QLabel(self.page)
        self.countrySuccessI.setPixmap(QtGui.QPixmap(r'resources\success.png'))
        self.countrySuccessI.setAlignment(Qt.AlignCenter)
        self.countryFailureI = QLabel(self.page)
        self.countryFailureI.setPixmap(QtGui.QPixmap(r'resources\failure.png'))
        self.countryFailureI.setAlignment(Qt.AlignCenter)
        self.topicsL = QLabel(self.page)
        self.topicsL.setText('Теми')
        self.topicsCCB = CheckedComboBox(self.page)
        self.topicsSuccessI = QLabel(self.page)
        self.topicsSuccessI.setPixmap(QtGui.QPixmap(r'resources\success.png'))
        self.topicsSuccessI.setAlignment(Qt.AlignCenter)
        self.topicsFailureI = QLabel(self.page)
        self.topicsFailureI.setPixmap(QtGui.QPixmap(r'resources\failure.png'))
        self.topicsFailureI.setAlignment(Qt.AlignCenter)
        self.keywordsL = QLabel(self.page)
        self.keywordsL.setText('Ключові слова')
        self.keywordsTB = QLineEdit(self.page)
        self.keywordsTB.setToolTip("У форматі: \"Keyword 1; Keyword 2\"")
        self.keywordsSuccessI = QLabel(self.page)
        self.keywordsSuccessI.setPixmap(QtGui.QPixmap(r'resources\success.png'))
        self.keywordsSuccessI.setAlignment(Qt.AlignCenter)
        self.keywordsFailureI = QLabel(self.page)
        self.keywordsFailureI.setPixmap(QtGui.QPixmap(r'resources\failure.png'))
        self.keywordsFailureI.setAlignment(Qt.AlignCenter)
        self.dateL = QLabel(self.page)
        self.dateL.setText('Дата')
        self.dateFromL = QLabel(self.page)
        self.dateFromL.setText('З')
        self.dateFromDP = QDateEdit(self.page)
        self.dateFromDP.setDate(QtCore.QDate(1900, 1, 1))
        self.dateToDP = QDateEdit(self.page)
        self.dateToL = QLabel(self.page)
        self.dateToL.setText('До')
        self.dateToDP.setDate(QtCore.QDate.currentDate())
        self.dateSuccessI = QLabel(self.page)
        self.dateSuccessI.setPixmap(QtGui.QPixmap(r'resources\success.png'))
        self.dateSuccessI.setAlignment(Qt.AlignCenter)
        self.dateFailureI = QLabel(self.page)
        self.dateFailureI.setPixmap(QtGui.QPixmap(r'resources\failure.png'))
        self.dateFailureI.setAlignment(Qt.AlignCenter)
        self.sourcesL = QLabel(self.page)
        self.sourcesL.setText('Джерела')
        self.sourcesCCB = CheckedComboBox(self.page)
        self.sourcesCCB.addItems(['Scopus', 'Google Scholar', 'CORE', 'Internal'])

        self.verifyB = QPushButton(self.page)
        self.verifyB.setText('Верифікувати')
        self.clearB = QPushButton(self.page)
        self.clearB.setText('Очистити')
        self.strictChB = QCheckBox(self.page)
        self.strictChB.setText('Строга відповідність')
        self.progressBar = QProgressBar(self.page)
        self.progressBar.setProperty("value", 0)

        self.resultsGrid = QTableView(self.page)
        self.resultsGrid.setSortingEnabled(True)

        self.affL.setGeometry(10, 10, 100, 30)
        self.affCB.setGeometry(120, 10, 400, 30)
        self.authorL.setGeometry(10, 50, 100, 30)
        self.authorCB.setGeometry(120, 50, 400, 30)
        self.hirshL.setGeometry(10, 90, 100, 30)
        self.hirshTB.setGeometry(120, 90, 330, 30)
        self.hirshSuccessI.setGeometry(460, 90, 30, 30)
        self.hirshFailureI.setGeometry(460, 90, 30, 30)
        self.citL.setGeometry(530, 90, 100, 30)
        self.citTB.setGeometry(640, 90, 330, 30)
        self.citSuccessI.setGeometry(980, 90, 30, 30)
        self.citFailureI.setGeometry(980, 90, 30, 30)
        self.titleL.setGeometry(10, 130, 100, 30)
        self.titleTB.setGeometry(120, 130, 330, 30)
        self.titleSuccessI.setGeometry(460, 130, 30, 30)
        self.titleFailureI.setGeometry(460, 130, 30, 30)
        self.topicsL.setGeometry(530, 130, 100, 30)
        self.topicsCCB.setGeometry(640, 130, 330, 30)
        self.topicsSuccessI.setGeometry(980, 130, 30, 30)
        self.topicsFailureI.setGeometry(980, 130, 30, 30)
        self.countryL.setGeometry(10, 170, 100, 30)
        self.countryCCB.setGeometry(120, 170, 330, 30)
        self.countrySuccessI.setGeometry(460, 170, 30, 30)
        self.countryFailureI.setGeometry(460, 170, 30, 30)
        self.cityL.setGeometry(530, 170, 100, 30)
        self.cityCCB.setGeometry(640, 170, 330, 30)
        self.citySuccessI.setGeometry(980, 170, 30, 30)
        self.cityFailureI.setGeometry(980, 170, 30, 30)
        self.keywordsL.setGeometry(10, 210, 100, 30)
        self.keywordsTB.setGeometry(120, 210, 330, 30)
        self.keywordsSuccessI.setGeometry(460, 210, 30, 30)
        self.keywordsFailureI.setGeometry(460, 210, 30, 30)
        self.dateL.setGeometry(530, 210, 100, 30)
        self.dateFromL.setGeometry(640, 210, 50, 30)
        self.dateFromDP.setGeometry(670, 210, 120, 30)
        self.dateToL.setGeometry(820, 210, 50, 30)
        self.dateToDP.setGeometry(850, 210, 120, 30)
        self.dateSuccessI.setGeometry(980, 210, 30, 30)
        self.dateFailureI.setGeometry(980, 210, 30, 30)
        self.publisherL.setGeometry(10, 250, 100, 30)
        self.publisherCCB.setGeometry(120, 250, 400, 30)
        self.publisherSuccessI.setGeometry(530, 250, 30, 30)
        self.publisherFailureI.setGeometry(530, 250, 30, 30)
        self.sourcesL.setGeometry(10, 290, 100, 30)
        self.sourcesCCB.setGeometry(120, 290, 140, 30)

        self.progressL = QLabel(self.page)
        self.progressL.setText('')
        self.progressL.setAlignment(Qt.AlignHCenter)
        self.progressL.setWordWrap(True)

        self.verifyB.setGeometry(10, 340, 100, 30)
        self.clearB.setGeometry(120, 340, 100, 30)
        self.strictChB.setGeometry(230, 340, 150, 30)
        self.progressBar.setGeometry(400, 340, 320, 30)
        self.progressL.setGeometry(400, 380, 300, 60)

        self.resultsGrid.setGeometry(10, 450, 1870, 495)

    def setup_events(self):
        self.verifyB.clicked.connect(self.on_verifyB_clicked)
        self.clearB.clicked.connect(self.on_clearB_clicked)

        self.affCB.currentTextChanged.connect(self.on_affCB_changed)
        self.countryCCB.activated.connect(self.on_countryCCB_activated)

        self.resultsGrid.doubleClicked.connect(self.on_resultsGrid_doubleClicked)

    def init_ui(self):
        self.countries = [a.country
                          for a in affiliations().group_by(Affiliation.country).order_by(Affiliation.country)
                          if a.country is not None]
        self.aff_objs = [a for a in affiliations().order_by(Affiliation.affiliation_name)]
        self.affiliations = [f'{a.affiliation_name} ({a.city}, {a.country})' for a in affiliations()
            .order_by(Affiliation.affiliation_name)]
        self.topics = [s.group for s in subjects().group_by(Subject.group).order_by(Subject.group)]

        self.topicsCCB.addItems(self.topics)
        self.affCB.addItems(self.affiliations)
        self.publisherCCB.addItems(self.affiliations)
        self.countryCCB.addItems(self.countries)
    # endregion

    # region EVENTS
    def on_clearB_clicked(self):
        self.clear()
        self.init_ui()
        self.authorCB.setCurrentIndex(-1)
        self.affCB.setCurrentIndex(-1)
        self.countryCCB.clearSelection()
        self.publisherCCB.clearSelection()
        self.topicsCCB.clearSelection()

    def on_affCB_changed(self, value):
        try:
            if self.affCB.currentIndex() != -1:
                idx = self.affCB.currentIndex()
                self.authorCB.clear()
                self.authors = {a.author_id: f'{a.name} ({a.author_id})' for a
                                in authors().join(AffiliationAuthor)
                                    .where(AffiliationAuthor.affiliation == self.aff_objs[idx])
                                    .switch(Author).order_by(Author.name)}
                self.authorCB.addItems(self.authors.values())
        except Exception as err:
            print(err)

    def on_countryCCB_activated(self):
        try:
            if self.countryCCB.hasSelection():
                self.cityCCB.clearSelection()
                self.cityCCB.clear()
                selected = [i.index().row() for i in self.countryCCB.getChecked()]
                items = [self.countries[i] for i in range(len(self.countries)) if i in selected]
                self.cities = {a.affiliation_id: a.city for a in affiliations().group_by(Affiliation.city)
                               if a.country in items}
                self.cityCCB.addItems(self.cities.values())
        except Exception as err:
            print(err)

    def on_verifyB_clicked(self):
        if self.verifyB.text() == 'Верифікувати':
            res = self.verify()
            if res:
                ret = QMessageBox.question(self.page, '', "Продовжити пошук в Інтернеті?",
                                           QMessageBox.Yes | QMessageBox.No)

                if ret == QMessageBox.Yes:
                    self.search()
        else:
            self.abort()

    def progress_bar_handler(self, value):
        with redrawLock:
            self.progressBar.setValue(value)

    def progress_bar_max_handler(self, maximum):
        try:
            with redrawLock:
                self.progressBar.setMaximum(maximum)
        except Exception as err:
            print(f'error: {err}')

    def results_handler(self):
        try:
            self.progressBar.setValue(0)
            self.progressBar.hide()
            self.progressL.hide()
            self.verifyB.setText('Верифікувати')
            self.enable()
            self.verify()
        except Exception as err:
            print(err)

    def update_handler(self):
        try:
            with updateLock:
                if self.updateThread is not None:
                    self.updateThread.terminate()

                self.updateThread = QThread()
                self.updater = Updater(self.update)
                self.updater.moveToThread(self.updateThread)
                self.updateThread.started.connect(self.updater.run)
                self.updateThread.start()
        except Exception as err:
            print(err)

    def progress_verification_handler(self, status):
        self.progressL.setText(status)

    def on_resultsGrid_doubleClicked(self, idx):
        uid = self.resultsGrid.model().index(idx.row(), 0).data()
        self.switch(uid, 'Публікації')

    # endregion
    # region HANDLERS

    def search(self):
        self.progressBar.show()
        self.progressL.show()
        self.disable()
        self.verifyB.setText('Зупинити')

        tokens = tokenize(self.author.surname, self.author.name)
        name = build_name(tokens)
        if self.author.scopus_id is not None:
            query = f'AU-ID({self.author.scopus_id})'
        else:
            query = ''
        sources = self.sourcesCCB.getCheckedTexts()
        authors = [self.author]

        wrapper = SignalsWrapper()
        wrapper.progress_signal.connect(self.progress_bar_handler)
        wrapper.set_max_signal.connect(self.progress_bar_max_handler)
        wrapper.status_signal.connect(self.progress_verification_handler)
        wrapper.results_signal.connect(self.results_handler)
        wrapper.update_signal.connect(self.update_handler)

        if self.parseThread is not None:
            self.parseThread.terminate()

        self.parseThread = QThread()
        self.parser = Parser(query, wrapper, coauthors=False, sources=sources, authors=authors)
        self.parser.moveToThread(self.parseThread)
        self.parseThread.started.connect(self.parser.run)
        self.parseThread.start()

    def abort(self):
        try:
            self.parser.abort()
        except Exception as err:
            print(err)

    def verify(self):
        try:
            if self.authorCB.currentIndex() == -1:
                return

            self.hide()

            self.auth_id = self.get_author()
            self.author = authors().where(Author.author_id == self.auth_id).get()
            self.verifiers = []

            self.verify_hirsh()
            self.verify_cit()
            self.build_date_verifier()
            self.build_title_verifier()
            self.build_keywords_verifier()
            self.build_topics_verifier()
            self.build_publishers_verifier()
            self.build_location_verifier()

            pubs = [p for p in publications().join(AuthorPublication).where(AuthorPublication.author == self.auth_id)]

            if not self.sourcesCCB.hasSelection():
                show_message('Не обрано джерела')
                return False
            sources = self.sourcesCCB.getCheckedTexts()
            print(sources)
            pubs = filter_publications_by_sources(pubs, sources)

            verified_pubs = []

            for p in pubs:
                pa = [a.affiliation_publication_id for a in affiliations_publications().join(Publication)
                    .where(AffiliationPublication.publication.publication_id == p.publication_id)]
                self.verifiers[0].verify(p, verified_pubs, pa)

            for v in self.verifiers:
                v.visualize()

            if any(verified_pubs):
                self.fill_pubs(verified_pubs)
                self.resultsGrid.show()
            else:
                self.resultsGrid.hide()

            return True
        except Exception as err:
            print(err)

    def verify_hirsh(self):
        if self.hirshTB.text() != '':
            hirsh = int(self.hirshTB.text())
            if hirsh == self.author.h_index:
                self.hirshSuccessI.show()
            else:
                self.hirshFailureI.show()

    def verify_cit(self):
        if self.citTB.text() != '':
            requested_cits = int(self.citTB.text())
            stored_cits = get_citations_count(self.author.author_id)
            if requested_cits == stored_cits:
                self.citSuccessI.show()
            else:
                self.citFailureI.show()

    def build_date_verifier(self):
        dateFrom = self.dateFromDP.date()
        dateTo = self.dateToDP.date()

        verifier = DateVerifier(self.strictChB.isChecked(), self.date_succeed, self.date_fail, dateFrom, dateTo)
        self.verifiers.append(verifier)

    def build_keywords_verifier(self):
        if self.keywordsTB.text() != '':
            keywords = self.keywordsTB.text().split('; ')

            verifier = KeywordsVerifier(self.strictChB.isChecked(), self.keywords_succeed, self.keywords_fail, keywords)
            self.verifiers[-1].set_next(verifier)
            self.verifiers.append(verifier)

    def build_title_verifier(self):
        if self.titleTB.text() != '':
            title = self.titleTB.text()

            verifier = TitleVerifier(self.strictChB.isChecked(), self.title_succeed,  self.title_fail, title)
            self.verifiers[-1].set_next(verifier)
            self.verifiers.append(verifier)

    def build_topics_verifier(self):
        if self.topicsCCB.hasSelection():
            selected = [i.index().row() for i in self.topicsCCB.getChecked()]
            tops = [self.topics[i] for i in range(len(self.topics)) if i in selected]

            verifier = TopicsVerifier(self.strictChB.isChecked(), self.topics_succeed, self.topics_fail, tops)
            self.verifiers[-1].set_next(verifier)
            self.verifiers.append(verifier)

    def build_publishers_verifier(self):
        if self.publisherCCB.hasSelection():
            selected = self.publisherCCB.getCheckedIndices()
            affs = []
            for i in selected:
                affs.append(self.aff_objs[i])

            verifier = PublishersVerifier(self.strictChB.isChecked(), self.publisher_succeed, self.publisher_fail, affs)
            self.verifiers[-1].set_next(verifier)
            self.verifiers.append(verifier)

    def build_location_verifier(self):
        if self.countryCCB.hasSelection():
            if self.cityCCB.hasSelection():
                selected = [i.index().row() for i in self.cityCCB.getChecked()]
                keys = list(self.cities.keys())
                cities = []
                for i in selected:
                    cities.append(self.cities[keys[i]])

                verifier = CitiesVerifier(self.strictChB.isChecked(), self.city_succeed, self.city_fail,
                                          cities)
            else:
                selected = [i.index().row() for i in self.countryCCB.getChecked()]
                countries = [self.countries[i] for i in range(len(self.countries)) if i in selected]
                verifier = CountriesVerifier(self.strictChB.isChecked(), self.country_succeed, self.country_fail,
                                             countries)

            self.verifiers[-1].set_next(verifier)
            self.verifiers.append(verifier)

    def get_author(self):
        value = self.authorCB.currentText()
        for k, v in self.authors.items():
            if v == value:
                return k

    def clear(self):
        try:
            self.hide()

            self.titleTB.clear()
            self.keywordsTB.clear()
            self.topicsCCB.clear()
            self.publisherCCB.clear()
            self.cityCCB.setCurrentIndex(-1)
            self.cityCCB.clear()
            self.countryCCB.clear()
            self.hirshTB.clear()
            self.citTB.clear()
            self.authorCB.setCurrentIndex(-1)
            self.authorCB.clear()
            self.sourcesCCB.clearSelection()
            self.sourcesCCB.selectAll()

            self.countryCCB.clearSelection()
            self.topicsCCB.clearSelection()
            self.affCB.setCurrentIndex(-1)
            self.publisherCCB.clearSelection()
        except Exception as err:
            print(err)
    # endregion

    # region GRAPHICS

    def fill_pubs(self, pub_list):
        items_list = []
        for row in pub_list:
            auth_list = get_authors_by_pub_id(row.publication_id)
            aff_list = get_affiliations_by_pub_id(row.publication_id)
            sub_list = get_subjects_by_publication_id(row.publication_id)
            sources = get_sources(row)
            items_list.append(
                [row.publication_id, row.title, row.abstract, row.url, row.cited_by_count, sub_list, row.keywords,
                 row.pub_date, auth_list, aff_list, sources])
        df = pd.DataFrame(items_list,
                              columns=['id', 'Назва', 'Анотація', 'Посилання', 'К-сть цитувань', 'Теми',
                                       'Ключові слова', 'Дата публікації', 'Автори', 'Організації', 'Джерела'])
        self.setModel(self.resultsGrid, df)

    def setModel(self, grid, df):
        model = TableModel(df)
        grid.setModel(model)
        header = grid.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        sizes = []
        for i in range(len(df.columns)):
            sizes.append(header.sectionSize(i))
        header.setSectionResizeMode(QHeaderView.Interactive)
        for i in range(len(df.columns)):
            header.resizeSection(i, sizes[i])

    def disable(self):
        self.affCB.setEnabled(False)
        self.authorCB.setEnabled(False)
        self.hirshTB.setEnabled(False)
        self.citTB.setEnabled(False)
        self.titleTB.setEnabled(False)
        self.topicsCCB.setEnabled(False)
        self.countryCCB.setEnabled(False)
        self.cityCCB.setEnabled(False)
        self.keywordsTB.setEnabled(False)
        self.dateFromDP.setEnabled(False)
        self.dateToDP.setEnabled(False)
        self.publisherCCB.setEnabled(False)
        self.sourcesCCB.setEnabled(False)

        self.clearB.setEnabled(False)
        self.strictChB.setEnabled(False)

    def enable(self):
        self.affCB.setEnabled(True)
        self.authorCB.setEnabled(True)
        self.hirshTB.setEnabled(True)
        self.citTB.setEnabled(True)
        self.titleTB.setEnabled(True)
        self.topicsCCB.setEnabled(True)
        self.countryCCB.setEnabled(True)
        self.cityCCB.setEnabled(True)
        self.keywordsTB.setEnabled(True)
        self.dateFromDP.setEnabled(True)
        self.dateToDP.setEnabled(True)
        self.publisherCCB.setEnabled(True)
        self.sourcesCCB.setEnabled(True)

        self.clearB.setEnabled(True)
        self.strictChB.setEnabled(True)

    def hide(self):
        self.title_hide()
        self.topics_hide()
        self.publisher_hide()
        self.country_hide()
        self.city_hide()
        self.hirsh_hide()
        self.cit_hide()
        self.keywords_hide()
        self.date_hide()
        self.resultsGrid.hide()
        self.progressBar.hide()
        self.progressL.hide()

    def title_succeed(self):
        self.titleFailureI.hide()
        self.titleSuccessI.show()

    def title_fail(self):
        self.titleFailureI.show()
        self.titleSuccessI.hide()

    def title_hide(self):
        self.titleFailureI.hide()
        self.titleSuccessI.hide()

    def topics_succeed(self):
        self.topicsFailureI.hide()
        self.topicsSuccessI.show()

    def topics_fail(self):
        self.topicsFailureI.show()
        self.topicsSuccessI.hide()

    def topics_hide(self):
        self.topicsFailureI.hide()
        self.topicsSuccessI.hide()

    def hirsh_succeed(self):
        self.hirshFailureI.hide()
        self.hirshSuccessI.show()

    def hirsh_fail(self):
        self.hirshFailureI.show()
        self.hirshSuccessI.hide()

    def hirsh_hide(self):
        self.hirshFailureI.hide()
        self.hirshSuccessI.hide()

    def cit_succeed(self):
        self.citFailureI.hide()
        self.citSuccessI.show()

    def cit_fail(self):
        self.citFailureI.show()
        self.citSuccessI.hide()

    def cit_hide(self):
        self.citFailureI.hide()
        self.citSuccessI.hide()

    def publisher_succeed(self):
        self.publisherFailureI.hide()
        self.publisherSuccessI.show()

    def publisher_fail(self):
        self.publisherFailureI.show()
        self.publisherSuccessI.hide()

    def publisher_hide(self):
        self.publisherFailureI.hide()
        self.publisherSuccessI.hide()

    def country_succeed(self):
        self.countryFailureI.hide()
        self.countrySuccessI.show()

    def country_fail(self):
        self.countryFailureI.show()
        self.countrySuccessI.hide()

    def country_hide(self):
        self.countryFailureI.hide()
        self.countrySuccessI.hide()

    def city_succeed(self):
        self.cityFailureI.hide()
        self.citySuccessI.show()

    def city_fail(self):
        self.cityFailureI.show()
        self.citySuccessI.hide()

    def city_hide(self):
        self.cityFailureI.hide()
        self.citySuccessI.hide()

    def keywords_succeed(self):
        self.keywordsFailureI.hide()
        self.keywordsSuccessI.show()

    def keywords_fail(self):
        self.keywordsFailureI.show()
        self.keywordsSuccessI.hide()

    def keywords_hide(self):
        self.keywordsFailureI.hide()
        self.keywordsSuccessI.hide()

    def date_succeed(self):
        self.dateFailureI.hide()
        self.dateSuccessI.show()

    def date_fail(self):
        self.dateFailureI.show()
        self.dateSuccessI.hide()

    def date_hide(self):
        self.dateFailureI.hide()
        self.dateSuccessI.hide()
    # endregion
