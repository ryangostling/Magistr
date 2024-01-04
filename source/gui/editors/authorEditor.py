# External
from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton

# Internal
from database.biblio.context import db
from database.biblio.models import Author, AffiliationAuthor, AuthorSubject, Affiliation, Subject
from database.biblio.selects import authors, affiliations, subjects, affiliations_authors, authors_subjects
from gui.misc.checkedComboBox import CheckedComboBox


class AuthorEditor(QMainWindow):
    # region SETUP
    def __init__(self, uid, filler):
        super().__init__()
        self.author = authors().where(Author.author_id == uid).get()
        self.filler = filler

        self.setup_ui(self)
        self.setup_events()
        self.init_relations()

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Редактор авторів')
        main_window.resize(500, 280)
        self.centralWidget = QWidget(main_window)
        self.intValidator = QIntValidator()

        self.idL = QLabel(self.centralWidget)
        self.idL.setText('id')
        self.idTB = QLineEdit(self.centralWidget)
        self.idTB.setText(str(self.author.author_id))
        self.idTB.setEnabled(False)
        self.nameL = QLabel(self.centralWidget)
        self.nameL.setText("Ім'я")
        self.nameTB = QLineEdit(self.centralWidget)
        self.nameTB.setText(str(self.author.name))
        self.hirshL = QLabel(self.centralWidget)
        self.hirshL.setText('Індекс Хірша')
        self.hirshTB = QLineEdit(self.centralWidget)
        self.hirshTB.setText(str(self.author.h_index))
        self.hirshTB.setValidator(self.intValidator)
        #self.citL = QLabel(self.centralWidget)
        #self.citL.setText('К-сть цитувань')
        #self.citTB = QLineEdit(self.centralWidget)
        #self.citTB.setValidator(self.intValidator)
        #self.citTB.setText(str(self.author.cited_by_count))
        self.affL = QLabel(self.centralWidget)
        self.affL.setText('Організації')
        self.affCCB = CheckedComboBox(self.centralWidget)
        self.subL = QLabel(self.centralWidget)
        self.subL.setText('Інтереси')
        self.subCCB = CheckedComboBox(self.centralWidget)

        self.updateB = QPushButton(self.centralWidget)
        self.updateB.setText('Зберегти')

        self.idL.setGeometry(10, 20, 100, 30)
        self.idTB.setGeometry(120, 20, 100, 30)
        self.nameL.setGeometry(10, 60, 100, 30)
        self.nameTB.setGeometry(120, 60, 370, 30)
        self.hirshL.setGeometry(10, 100, 100, 30)
        self.hirshTB.setGeometry(120, 100, 100, 30)
        #self.citL.setGeometry(230, 100, 100, 30)
        #self.citTB.setGeometry(340, 100, 100, 30)
        self.affL.setGeometry(10, 140, 100, 30)
        self.affCCB.setGeometry(120, 140, 370, 30)
        self.subL.setGeometry(10, 180, 100, 30)
        self.subCCB.setGeometry(120, 180, 370, 30)

        self.updateB.setGeometry(160, 230, 200, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.updateB.clicked.connect(self.on_updateB_clicked)
    # endregion

    # region EVENTS
    def on_updateB_clicked(self):
        try:
            name = self.nameTB.text()
            if name == '':
                return

            with db.atomic():
                self.author.name = name

                if self.hirshTB.text() != '' and int(self.hirshTB.text()) >= 0:
                    self.author.h_index = int(self.hirshTB.text())
                else:
                    self.author.h_index = 0
                '''
                if self.citTB.text() != '' and int(self.citTB.text()) >= 0:
                    self.author.cited_by_count = int(self.citTB.text())
                else:
                    self.author.cited_by_count = 0
                '''
                self.author.save()

                AuthorSubject.delete().where(AuthorSubject.author == self.author).execute()
                AffiliationAuthor.delete().where(AffiliationAuthor.author == self.author).execute()

                for i in self.subCCB.getCheckedIndices():
                    AuthorSubject.create(author_subject_id=self.ids['subject'], author=self.author,
                                         subject=self.sub_objs[i])
                    self.ids['subject'] += 1

                for i in self.affCCB.getCheckedIndices():
                    AffiliationAuthor.create(affiliation_author_id=self.ids['affiliation'], author=self.author,
                                             affiliation=self.aff_objs[i])
                    self.ids['affiliation'] += 1

                self.filler(self.author.author_id)

                self.close()
        except Exception as err:
            print(err)
    # endregion

    # region HANDLERS
    def init_relations(self):
        self.author_subjects = [ass.subject.full_title for ass in authors_subjects().join(Subject)
            .where(AuthorSubject.author == self.author)]
        self.sub_objs = [s for s in subjects().order_by(Subject.full_title)]
        self.subjects = [s.full_title for s in self.sub_objs]
        self.subCCB.addItems(self.subjects)
        for i in range(len(self.subjects)):
            if self.subjects[i] in self.author_subjects:
                self.subCCB.handleItemPressed(self.subCCB.model().index(i, 0))

        self.author_affiliations = [af.affiliation for af in affiliations_authors()
            .where(AffiliationAuthor.author == self.author)]
        self.aff_objs = [a for a in affiliations().order_by(Affiliation.affiliation_name)]
        self.affiliations = [f'{a.affiliation_name} ({a.city}, {a.country})' for a in affiliations()
            .order_by(Affiliation.affiliation_name)]
        self.affCCB.addItems(self.affiliations)
        for i in range(len(self.affiliations)):
            if self.aff_objs[i] in self.author_affiliations:
                self.affCCB.handleItemPressed(self.affCCB.model().index(i, 0))

        self.ids = {}
        if len(affiliations_authors()) != 0:
            self.ids['affiliation'] = affiliations_authors().order_by(AffiliationAuthor.affiliation_author_id.desc()) \
                                          .get().affiliation_author_id + 1
        else:
            self.ids['affiliation'] = 1

        if len(authors_subjects()) != 0:
            self.ids['subject'] = authors_subjects().order_by(AuthorSubject.author_subject_id.desc()) \
                                      .get().author_subject_id + 1
        else:
            self.ids['subject'] = 1
    # endregion
