# External
from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit, QDateEdit, QComboBox, QPushButton

# Internal
from database.biblio.context import db
from database.biblio.models import AffiliationAuthor, Author, Publication, PublicationSubject, AffiliationPublication, \
    AuthorPublication, Subject, Affiliation
from database.biblio.selects import affiliations_authors, authors, publications, subjects, affiliations, authors_publications,\
    affiliations_publications, publications_subjects
from gui.misc.checkedComboBox import CheckedComboBox


class PublicationEditor(QMainWindow):
    # region SETUP
    def __init__(self, uid, filler):
        self.lock = True
        super().__init__()
        self.publication = publications().where(Publication.publication_id == uid).get()
        self.filler = filler

        self.setup_ui(self)
        self.setup_events()

        self.init_relations()
        self.lock = False

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Редактор публікацій')
        main_window.resize(530, 670)
        self.centralWidget = QWidget(main_window)
        self.intValidator = QIntValidator()

        self.idL = QLabel(self.centralWidget)
        self.idL.setText('id')
        self.idTB = QLineEdit(self.centralWidget)
        self.idTB.setText(str(self.publication.publication_id))
        self.idTB.setEnabled(False)
        self.titleL = QLabel(self.centralWidget)
        self.titleL.setText("Назва")
        self.titleTB = QLineEdit(self.centralWidget)
        self.titleTB.setText(str(self.publication.title))
        self.abstractL = QLabel(self.centralWidget)
        self.abstractL.setText("Анотація")
        self.abstractRTB = QTextEdit(self.centralWidget)
        self.abstractRTB.setText(str(self.publication.abstract))
        self.keywordsL = QLabel(self.centralWidget)
        self.keywordsL.setText("Ключові слова")
        self.keywordsTB = QLineEdit(self.centralWidget)
        self.keywordsTB.setText(str(self.publication.keywords))
        self.dateL = QLabel(self.centralWidget)
        self.dateL.setText('Дата публікації')
        self.dateDP = QDateEdit(self.centralWidget)
        self.dateDP.setDate(self.publication.pub_date)
        self.citL = QLabel(self.centralWidget)
        self.citL.setText('К-сть цитувань')
        self.citTB = QLineEdit(self.centralWidget)
        self.citTB.setValidator(self.intValidator)
        self.citTB.setText(str(self.publication.cited_by_count))
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
        self.urlTB.setText(str(self.publication.url))

        self.affSearchL = QLabel(self.centralWidget)
        self.affSearchL.setText('Організація')
        self.affSearchCB = QComboBox(self.centralWidget)
        self.authSearchL = QLabel(self.centralWidget)
        self.authSearchL.setText('Пошук автора')
        self.authSearchCB = QComboBox(self.centralWidget)

        self.updateB = QPushButton(self.centralWidget)
        self.updateB.setText('Зберегти')

        self.idL.setGeometry(10, 20, 100, 30)
        self.idTB.setGeometry(120, 20, 100, 30)
        self.titleL.setGeometry(10, 60, 100, 30)
        self.titleTB.setGeometry(120, 60, 400, 30)
        self.abstractL.setGeometry(10, 100, 100, 30)
        self.abstractRTB.setGeometry(120, 100, 400, 140)
        self.keywordsL.setGeometry(10, 250, 100, 30)
        self.keywordsTB.setGeometry(120, 250, 400, 30)
        self.dateL.setGeometry(10, 290, 100, 30)
        self.dateDP.setGeometry(120, 290, 100, 30)
        self.citL.setGeometry(230, 290, 100, 30)
        self.citTB.setGeometry(340, 290, 100, 30)
        self.affL.setGeometry(10, 330, 100, 30)
        self.affCCB.setGeometry(120, 330, 400, 30)
        self.subL.setGeometry(10, 370, 100, 30)
        self.subCCB.setGeometry(120, 370, 400, 30)
        self.selectedL.setGeometry(10, 410, 100, 30)
        self.selectedCCB.setGeometry(120, 410, 400, 30)
        self.urlL.setGeometry(10, 450, 100, 30)
        self.urlTB.setGeometry(120, 450, 400, 30)

        self.affSearchL.setGeometry(10, 530, 100, 30)
        self.affSearchCB.setGeometry(120, 530, 400, 30)
        self.authSearchL.setGeometry(10, 570, 100, 30)
        self.authSearchCB.setGeometry(120, 570, 400, 30)

        self.updateB.setGeometry(175, 620, 200, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.updateB.clicked.connect(self.on_updateB_clicked)
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

    def on_updateB_clicked(self):
        title = self.titleTB.text()
        if title == '' or not self.selectedCCB.hasSelection():
            return

        try:
            with db.atomic():
                self.publication.title = title

                self.publication.abstract = self.abstractRTB.toPlainText()
                self.publication.keywords = self.keywordsTB.text()
                self.publication.url = self.urlTB.text()
                if self.citTB.text() != '' and int(self.citTB.text()) >= 0:
                    self.publication.cited_by_count = int(self.citTB.text())
                else:
                    self.publication.cited_by_count = 0
                self.publication.pub_date = self.dateDP.date().toPyDate()

                alternative_titles = self.publication.alternative_titles.split(' | ')
                if not any(filter(lambda t: title.lower() == t.lower, alternative_titles)):
                    alternative_titles.append(title)
                    self.publication.alternative_titles = ' | '.join(alternative_titles)

                self.publication.save()

                AuthorPublication.delete().where(AuthorPublication.publication == self.publication).execute()
                AffiliationPublication.delete().where(AffiliationPublication.publication == self.publication).execute()
                PublicationSubject.delete().where(PublicationSubject.publication == self.publication).execute()

                for i in self.subCCB.getCheckedIndices():
                    PublicationSubject.create(publication_subject_id=self.ids['subject'], publication=self.publication,
                                         subject=self.sub_objs[i])
                    self.ids['subject'] += 1

                for i in self.affCCB.getCheckedIndices():
                    AffiliationPublication.create(affiliation_publication_id=self.ids['affiliation'],
                                             publication=self.publication, affiliation=self.aff_objs[i])
                    self.ids['affiliation'] += 1

                for i in self.selectedCCB.getCheckedIndices():
                    AuthorPublication.create(author_publication_id=self.ids['author'],
                                             publication=self.publication, author=self.auth_objs[i])
                    self.ids['author'] += 1

                self.filler(self.publication.publication_id)
                self.close()
        except Exception as err:
            print(err)

    # endregion

    # region HANDLERS
    def init_relations(self):
        self.pub_subjects = [ps.subject.full_title for ps in publications_subjects().join(Subject)
            .where(PublicationSubject.publication == self.publication)]
        self.sub_objs = [s for s in subjects().order_by(Subject.full_title)]
        self.subjects = [s.full_title for s in self.sub_objs]
        self.subCCB.addItems(self.subjects)
        for i in range(len(self.subjects)):
            if self.subjects[i] in self.pub_subjects:
                self.subCCB.handleItemPressed(self.subCCB.model().index(i, 0))

        self.pub_affiliations = [ap.affiliation for ap in affiliations_publications()
            .where(AffiliationPublication.publication == self.publication)]
        self.aff_objs = [a for a in affiliations().order_by(Affiliation.affiliation_name)]
        self.affiliations = [f'{a.affiliation_name} ({a.city}, {a.country})' for a in affiliations()
            .order_by(Affiliation.affiliation_name)]
        self.affCCB.addItems(self.affiliations)
        for i in range(len(self.affiliations)):
            if self.aff_objs[i] in self.pub_affiliations:
                self.affCCB.handleItemPressed(self.affCCB.model().index(i, 0))

        self.pub_authors = [ap.author for ap in authors_publications()
            .where(AuthorPublication.publication == self.publication)]
        self.auth_objs = [a for a in authors().order_by(Author.name) if a in self.pub_authors]
        self.selected_authors = [f'{a.name} ({a.author_id})' for a in authors()
            .order_by(Author.name) if a in self.pub_authors]
        self.authors = [f'{a.name} ({a.author_id})' for a in authors()
            .order_by(Author.name)]
        self.selectedCCB.addItems(self.selected_authors)
        self.selectedCCB.selectAll()

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
