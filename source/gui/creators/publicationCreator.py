# External
from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit, QDateEdit, QComboBox, QPushButton

# Internal
from database.biblio.context import db
from database.biblio.models import AffiliationAuthor, Author, Publication, PublicationSubject, AffiliationPublication, \
    AuthorPublication, Subject, Affiliation
from database.biblio.selects import affiliations_authors, authors, publications, subjects, affiliations, authors_publications, \
    affiliations_publications, publications_subjects
from gui.misc.checkedComboBox import CheckedComboBox
from gui.misc.messageBox import show_message


class PublicationCreator(QMainWindow):
    # region SETUP
    def __init__(self, filler):
        self.lock = True
        super().__init__()
        self.filler = filler

        self.setup_ui(self)
        self.setup_events()

        self.init_relations()
        self.lock = False

        self.clear()

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Конструктор публікацій')
        main_window.resize(530, 630)
        self.centralWidget = QWidget(main_window)
        self.intValidator = QIntValidator()

        self.titleL = QLabel(self.centralWidget)
        self.titleL.setText("Назва")
        self.titleTB = QLineEdit(self.centralWidget)
        self.abstractL = QLabel(self.centralWidget)
        self.abstractL.setText("Анотація")
        self.abstractRTB = QTextEdit(self.centralWidget)
        self.keywordsL = QLabel(self.centralWidget)
        self.keywordsL.setText("Ключові слова")
        self.keywordsTB = QLineEdit(self.centralWidget)
        self.dateL = QLabel(self.centralWidget)
        self.dateL.setText('Дата публікації')
        self.dateDP = QDateEdit(self.centralWidget)
        self.citL = QLabel(self.centralWidget)
        self.citL.setText('К-сть цитувань')
        self.citTB = QLineEdit(self.centralWidget)
        self.citTB.setValidator(self.intValidator)
        self.affL = QLabel(self.centralWidget)
        self.affL.setText('Видавці')
        self.affCCB = CheckedComboBox(self.centralWidget)
        self.subL = QLabel(self.centralWidget)
        self.subL.setText('Теми')
        self.subCCB = CheckedComboBox(self.centralWidget)
        self.selectedL = QLabel(self.centralWidget)
        self.selectedL.setText('Автори')
        self.selectedCCB = CheckedComboBox(self.centralWidget)
        self.urlL = QLabel(self.centralWidget)
        self.urlL.setText('Посилання')
        self.urlTB = QLineEdit(self.centralWidget)

        self.affSearchL = QLabel(self.centralWidget)
        self.affSearchL.setText('Організація')
        self.affSearchCB = QComboBox(self.centralWidget)
        self.authSearchL = QLabel(self.centralWidget)
        self.authSearchL.setText('Пошук автора')
        self.authSearchCB = QComboBox(self.centralWidget)

        self.createB = QPushButton(self.centralWidget)
        self.createB.setText('Зберегти')

        self.titleL.setGeometry(10, 20, 100, 30)
        self.titleTB.setGeometry(120, 20, 400, 30)
        self.abstractL.setGeometry(10, 60, 100, 30)
        self.abstractRTB.setGeometry(120, 60, 400, 140)
        self.keywordsL.setGeometry(10, 210, 100, 30)
        self.keywordsTB.setGeometry(120, 210, 400, 30)
        self.dateL.setGeometry(10, 250, 100, 30)
        self.dateDP.setGeometry(120, 250, 100, 30)
        self.citL.setGeometry(230, 250, 100, 30)
        self.citTB.setGeometry(340, 250, 100, 30)
        self.affL.setGeometry(10, 290, 100, 30)
        self.affCCB.setGeometry(120, 290, 400, 30)
        self.subL.setGeometry(10, 330, 100, 30)
        self.subCCB.setGeometry(120, 330, 400, 30)
        self.selectedL.setGeometry(10, 370, 100, 30)
        self.selectedCCB.setGeometry(120, 370, 400, 30)
        self.urlL.setGeometry(10, 410, 100, 30)
        self.urlTB.setGeometry(120, 410, 400, 30)

        self.affSearchL.setGeometry(10, 490, 100, 30)
        self.affSearchCB.setGeometry(120, 490, 400, 30)
        self.authSearchL.setGeometry(10, 530, 100, 30)
        self.authSearchCB.setGeometry(120, 530, 400, 30)

        self.createB.setGeometry(175, 580, 200, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.createB.clicked.connect(self.on_createB_clicked)
        self.affSearchCB.currentTextChanged.connect(self.on_affSearchCB_changed)
        self.authSearchCB.currentTextChanged.connect(self.on_authSearchCB_changed)
    # endregion

    # region EVENTS
    def on_affSearchCB_changed(self):
        try:
            idx = self.affSearchCB.currentIndex()
            sel_aff = self.aff_objs[idx]

            self.search_auths = [a.author for a in affiliations_authors().join(Author)
                .where(AffiliationAuthor.affiliation == sel_aff).order_by(Author.name)]
            aa = [f'{a.author.name} ({a.author.author_id})' for a in affiliations_authors().join(Author)
                .where(AffiliationAuthor.affiliation == sel_aff).order_by(Author.name)]
            self.lock = True
            self.authSearchCB.clear()
            self.authSearchCB.addItems(aa)
            self.authSearchCB.setCurrentIndex(-1)
            self.lock = False
        except Exception as err:
            print(err)

    def on_authSearchCB_changed(self):
        try:
            if self.authSearchCB.currentIndex() == -1 or self.lock:
                return

            idx = self.authSearchCB.currentIndex()
            sel = self.search_auths[idx]

            if sel not in self.auth_objs:
                self.selectedCCB.addItem(f'{sel.name} ({sel.author_id})')
                self.auth_objs.append(sel)
                self.selectedCCB.selectLast()
        except Exception as err:
            print(err)

    def on_createB_clicked(self):
        title = self.titleTB.text()
        if title == '' or not self.selectedCCB.hasSelection():
            return
        if any(publications().where(Publication.title == title)):
            show_message('Публікація з такою назвою вже існує')
            return

        try:
            with db.atomic():
                if len(authors()) != 0:
                    uid = publications().order_by(Publication.publication_id.desc()) \
                              .get().publication_id + 1
                else:
                    uid = 1
                abstract = self.abstractRTB.toPlainText()
                keywords = self.keywordsTB.text()
                url = self.urlTB.text()
                if self.citTB.text() != '' and int(self.citTB.text()) >= 0:
                    cited_by_count = int(self.citTB.text())
                else:
                    cited_by_count = 0
                pub_date = self.dateDP.date().toPyDate()

                publication = Publication.create(publication_id=uid, title=title, abstract=abstract, keywords=keywords,
                                                 url=url, cited_by_count=cited_by_count, pub_date=pub_date,
                                                 alternative_titles=title)
                print('here')
                for i in self.subCCB.getCheckedIndices():
                    PublicationSubject.create(publication_subject_id=self.ids['subject'], publication=publication,
                                              subject=self.sub_objs[i])
                    self.ids['subject'] += 1

                for i in self.affCCB.getCheckedIndices():
                    AffiliationPublication.create(affiliation_publication_id=self.ids['affiliation'],
                                                  publication=publication, affiliation=self.aff_objs[i])
                    self.ids['affiliation'] += 1

                for i in self.selectedCCB.getCheckedIndices():
                    AuthorPublication.create(author_publication_id=self.ids['author'],
                                             publication=publication, author=self.auth_objs[i])
                    self.ids['author'] += 1

                self.filler(uid)
                self.close()
        except Exception as err:
            print(err)

    # endregion

    # region HANDLERS
    def init_relations(self):
        self.sub_objs = [s for s in subjects().order_by(Subject.full_title)]
        self.subjects = [s.full_title for s in self.sub_objs]
        self.subCCB.addItems(self.subjects)

        self.aff_objs = [a for a in affiliations().order_by(Affiliation.affiliation_name)]
        self.affiliations = [f'{a.affiliation_name} ({a.city}, {a.country})' for a in affiliations()
            .order_by(Affiliation.affiliation_name)]
        self.affCCB.addItems(self.affiliations)

        self.auth_objs = []
        self.authors = [f'{a.name} ({a.author_id})' for a in authors()
            .order_by(Author.name)]

        self.affSearchCB.addItems(self.affiliations)

        self.ids = {}
        self.ids['author'] = authors_publications().order_by(AuthorPublication.author_publication_id.desc()) \
                                      .get().author_publication_id + 1
        self.ids['affiliation'] = affiliations_publications()\
                                      .order_by(AffiliationPublication.affiliation_publication_id.desc()) \
                                      .get().affiliation_publication_id + 1
        self.ids['subject'] = publications_subjects().order_by(PublicationSubject.publication_subject_id.desc()) \
                                  .get().publication_subject_id + 1
    # endregion

    # region HANDLERS
    def clear(self):
        self.titleTB.clear()
        self.abstractRTB.clear()
        self.keywordsTB.clear()
        self.citTB.clear()
        self.affCCB.clearSelection()
        self.subCCB.clearSelection()
        self.selectedCCB.clearSelection()
        self.urlTB.clear()
    # endregion