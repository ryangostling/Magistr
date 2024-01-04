# External
from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton

# Internal
from database.biblio.context import db
from database.biblio.models import Author, AffiliationAuthor, AuthorSubject, Affiliation, Subject
from database.biblio.selects import authors, affiliations, subjects, affiliations_authors, authors_subjects
from gui.misc.checkedComboBox import CheckedComboBox


class AuthorCreator(QMainWindow):
    # region SETUP
    def __init__(self, filler):
        super().__init__()
        self.filler = filler

        self.setup_ui(self)
        self.setup_events()
        self.init_relations()

        self.clear()

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Конструктор авторів')
        main_window.resize(500, 240)
        self.centralWidget = QWidget(main_window)
        self.intValidator = QIntValidator()

        self.nameL = QLabel(self.centralWidget)
        self.nameL.setText("Ім'я")
        self.nameTB = QLineEdit(self.centralWidget)
        self.hirshL = QLabel(self.centralWidget)
        self.hirshL.setText('Індекс Хірша')
        self.hirshTB = QLineEdit(self.centralWidget)
        self.hirshTB.setValidator(self.intValidator)
        # self.citL = QLabel(self.centralWidget)
        # self.citL.setText('К-сть цитувань')
        # self.citTB = QLineEdit(self.centralWidget)
        # self.citTB.setValidator(self.intValidator)
        # self.citTB.setText(str(self.author.cited_by_count))
        self.affL = QLabel(self.centralWidget)
        self.affL.setText('Організації')
        self.affCCB = CheckedComboBox(self.centralWidget)
        self.subL = QLabel(self.centralWidget)
        self.subL.setText('Інтереси')
        self.subCCB = CheckedComboBox(self.centralWidget)

        self.createB = QPushButton(self.centralWidget)
        self.createB.setText('Додати')

        self.nameL.setGeometry(10, 20, 100, 30)
        self.nameTB.setGeometry(120, 20, 370, 30)
        self.hirshL.setGeometry(10, 60, 100, 30)
        self.hirshTB.setGeometry(120, 60, 100, 30)
        #self.citL.setGeometry(230, 60, 100, 30)
        #self.citTB.setGeometry(340, 60, 100, 30)
        self.affL.setGeometry(10, 100, 100, 30)
        self.affCCB.setGeometry(120, 100, 370, 30)
        self.subL.setGeometry(10, 140, 100, 30)
        self.subCCB.setGeometry(120, 140, 370, 30)

        self.createB.setGeometry(160, 190, 200, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.createB.clicked.connect(self.on_createB_clicked)
    # endregion

    # region EVENTS
    def on_createB_clicked(self):
        try:
            name = self.nameTB.text()
            if name == '':
                return

            with db.atomic():
                if len(authors()) != 0:
                    uid = authors().order_by(Author.author_id.desc()) \
                              .get().author_id + 1
                else:
                    uid = 1
                if self.hirshTB.text() != '' and int(self.hirshTB.text()) >= 0:
                    h_index = int(self.hirshTB.text())
                else:
                    h_index = 0
                '''
                if self.citTB.text() != '' and int(self.citTB.text()) >= 0:
                    cited_by_count = int(self.citTB.text())
                else:
                    cited_by_count = 0
                '''

                author = Author.create(author_id=uid, name=name, h_index=h_index, cited_by_count=0)

                for i in self.subCCB.getCheckedIndices():
                    AuthorSubject.create(author_subject_id=self.ids['subject'], author=author,
                                         subject=self.sub_objs[i])
                    self.ids['subject'] += 1

                for i in self.affCCB.getCheckedIndices():
                    AffiliationAuthor.create(affiliation_author_id=self.ids['affiliation'], author=author,
                                             affiliation=self.aff_objs[i])
                    self.ids['affiliation'] += 1

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

        self.ids = {}
        if len(affiliations_authors()) != 0:
            self.ids['affiliation'] = affiliations_authors().order_by(AffiliationAuthor.affiliation_author_id.desc())\
                .get().affiliation_author_id + 1
        else:
            self.ids['affiliation'] = 1

        if len(authors_subjects()) != 0:
            self.ids['subject'] = authors_subjects().order_by(AuthorSubject.author_subject_id.desc()) \
                .get().author_subject_id + 1
        else:
            self.ids['subject'] = 1
    # endregion

    # region HANDLERS
    def clear(self):
        self.nameTB.clear()
        self.hirshTB.clear()
        self.affCCB.clearSelection()
        self.subCCB.clearSelection()
    # endregion