# External
from fuzzywuzzy import fuzz
from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QDateEdit

# Internal
from database.biblio.models import Affiliation, Subject, Publication
from database.biblio.selects import affiliations, subjects, publications, affiliations_publications, \
    publications_subjects
from gui.misc.checkedComboBox import CheckedComboBox
from misc.filters import filter_publications_by_title, filter_publications_by_authors, filter_publications_by_sources
from gui.misc.messageBox import show_message

class PublicationFilterWindow(QMainWindow):
    # region SETUP
    def __init__(self, set_model):
        super().__init__()

        self.aff_objs = [a for a in affiliations().order_by(Affiliation.affiliation_name)]
        self.affiliations = [f'{a.affiliation_name} ({a.city}, {a.country})' for a in affiliations()
            .order_by(Affiliation.affiliation_name)]
        self.sub_obj = [s for s in subjects().group_by(Subject.group).order_by(Subject.group)]
        self.subjects = [s.group for s in subjects().group_by(Subject.group).order_by(Subject.group)]

        self.setup_ui(self)
        self.setup_events()
        self.set_model = set_model
        self.clear()

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Фільтр публікацій')
        main_window.resize(530, 400)
        self.centralWidget = QWidget(main_window)
        self.intValidator = QIntValidator()

        self.titleL = QLabel(self.centralWidget)
        self.titleL.setText('Назва')
        self.titleTB = QLineEdit(self.centralWidget)
        self.keywordsL = QLabel(self.centralWidget)
        self.keywordsL.setText('Ключові слова')
        self.keywordsTB = QLineEdit(self.centralWidget)
        self.keywordsTB.setToolTip("У форматі: \"Keyword 1; Keyword 2\"")

        self.authorsL = QLabel(self.centralWidget)
        self.authorsL.setText('Автори')
        self.authorsTB = QLineEdit(self.centralWidget)
        self.authorsTB.setToolTip("У форматі: \"Petrenko P.; Ivanenenko I.\"")

        self.affiliationsL = QLabel(self.centralWidget)
        self.affiliationsL.setText('Видавці')
        self.affiliationsCCB = CheckedComboBox(self.centralWidget)
        self.affiliationsCCB.addItems(self.affiliations)

        self.subjectsL = QLabel(self.centralWidget)
        self.subjectsL.setText('Теми')
        self.subjectsCCB = CheckedComboBox(self.centralWidget)
        self.subjectsCCB.addItems(self.subjects)

        self.dateL = QLabel(self.centralWidget)
        self.dateL.setText('Дата публікації')
        self.dateFromL = QLabel(self.centralWidget)
        self.dateFromL.setText('Від')
        self.dateFromDP = QDateEdit(self.centralWidget)
        self.dateFromDP.setDate(QtCore.QDate(1900, 1, 1))
        self.dateToL = QLabel(self.centralWidget)
        self.dateToL.setText('До')
        self.dateToDP = QDateEdit(self.centralWidget)
        self.dateToDP.setDate(QtCore.QDate.currentDate())

        self.citL = QLabel(self.centralWidget)
        self.citL.setText('К-сть цитувань')
        self.citFromL = QLabel(self.centralWidget)
        self.citFromL.setText('Від')
        self.citFromTB = QLineEdit(self.centralWidget)
        self.citFromTB.setValidator(self.intValidator)
        self.citFromTB.setText('0')
        self.citToL = QLabel(self.centralWidget)
        self.citToL.setText('До')
        self.citToTB = QLineEdit(self.centralWidget)
        self.citToTB.setValidator(self.intValidator)
        self.citToTB.setText('1000')
        self.sourcesL = QLabel(self.centralWidget)
        self.sourcesL.setText('Джерела')
        self.sourcesCCB = CheckedComboBox(self.centralWidget)
        self.sourcesCCB.addItems(['Scopus', 'Google Scholar', 'CORE', 'Internal'])

        self.acceptB = QPushButton(self.centralWidget)
        self.acceptB.setText('Фільтрувати')
        self.clearB = QPushButton(self.centralWidget)
        self.clearB.setText('Очистити')

        self.titleL.setGeometry(10, 20, 100, 30)
        self.titleTB.setGeometry(120, 20, 400, 30)
        self.keywordsL.setGeometry(10, 60, 100, 30)
        self.keywordsTB.setGeometry(120, 60, 400, 30)
        self.authorsL.setGeometry(10, 100, 100, 30)
        self.authorsTB.setGeometry(120, 100, 400, 30)
        self.affiliationsL.setGeometry(10, 140, 100, 30)
        self.affiliationsCCB.setGeometry(120, 140, 400, 30)
        self.subjectsL.setGeometry(10, 180, 100, 30)
        self.subjectsCCB.setGeometry(120, 180, 400, 30)
        self.dateL.setGeometry(10, 220, 100, 30)
        self.dateFromL.setGeometry(120, 220, 50, 30)
        self.dateFromDP.setGeometry(160, 220, 100, 30)
        self.dateToL.setGeometry(290, 220, 50, 30)
        self.dateToDP.setGeometry(330, 220, 100, 30)
        self.citL.setGeometry(10, 260, 100, 30)
        self.citFromL.setGeometry(120, 260, 50, 30)
        self.citFromTB.setGeometry(160, 260, 100, 30)
        self.citToL.setGeometry(290, 260, 50, 30)
        self.citToTB.setGeometry(330, 260, 100, 30)
        self.sourcesL.setGeometry(10, 300, 100, 30)
        self.sourcesCCB.setGeometry(120, 300, 140, 30)

        self.acceptB.setGeometry(140, 350, 100, 30)
        self.clearB.setGeometry(330, 350, 100, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.acceptB.clicked.connect(self.on_acceptB_clicked)
        self.clearB.clicked.connect(self.on_clearB_clicked)
    # endregion

    # region EVENTS
    def on_acceptB_clicked(self):
        try:
            pubs = publications()

            if self.citFromTB.text() != '':
                pubs = pubs.where(Publication.cited_by_count >= int(self.citFromTB.text()))

            if self.citToTB.text() != '':
                pubs = pubs.where(Publication.cited_by_count <= int(self.citToTB.text()))

            from_date = self.dateFromDP.date().toPyDate()
            to_date = self.dateToDP.date().toPyDate()
            pubs = pubs.where((Publication.pub_date >= from_date) & (Publication.pub_date <= to_date))

            pubs = [p for p in pubs]
            if not self.sourcesCCB.hasSelection():
                show_message('Не обрано джерела')
                return
            sources = self.sourcesCCB.getCheckedTexts()
            print(sources)
            pubs = filter_publications_by_sources(pubs, sources)

            if self.affiliationsCCB.hasSelection():
                selected = self.affiliationsCCB.getCheckedIndices()
                objs = [self.aff_objs[i] for i in selected]
                pubs = list(dict.fromkeys([p.publication for p in affiliations_publications() if p.affiliation in objs
                                            and p.publication in pubs]))

            if self.keywordsTB.text() != '':
                selected_kws = self.keywordsTB.text().split('; ')
                pubs_list = []
                for p in pubs:
                    for k in p.keywords.split('; '):
                        flag = False
                        for s in selected_kws:
                            if fuzz.ratio(k.lower(), s.lower()) >= 60:
                                pubs_list.append(p)
                                flag = True
                                break
                        if flag:
                            break
                pubs = pubs_list

            if self.authorsTB.text() != '':
                selected_authors = self.authorsTB.text().split('; ')
                pubs = filter_publications_by_authors(pubs, selected_authors)

            if self.subjectsCCB.hasSelection():
                selected = self.subjectsCCB.getCheckedIndices()
                objs = [self.sub_obj[i] for i in selected]
                pubs = list(dict.fromkeys([p.publication for p in publications_subjects() if p.subject in objs
                                            and p.publication in pubs]))

            title = self.titleTB.text()
            if title != '':
                pubs = filter_publications_by_title(pubs, title)

            if len(pubs) == 0:
                show_message('Не знайдено жодного запису')
            else:
                self.set_model(pubs)
        except Exception as err:
            print(err)

    def on_clearB_clicked(self):
        self.clear()
    # endregion

    # region HANDLERS

    def clear(self):
        self.titleTB.clear()
        self.keywordsTB.clear()
        self.authorsTB.clear()
        self.affiliationsCCB.clearSelection()
        self.subjectsCCB.clearSelection()
        self.dateFromDP.setDate(QtCore.QDate(1900, 1, 1))
        self.dateToDP.setDate(QtCore.QDate.currentDate())
        self.citFromTB.setText('0')
        self.citToTB.setText('1000')
        self.sourcesCCB.clearSelection()
        self.sourcesCCB.selectAll()
    # endregion