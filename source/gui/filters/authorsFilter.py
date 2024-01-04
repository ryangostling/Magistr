# External
from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton

# Internal
from database.biblio.models import Author, Affiliation, Subject
from database.biblio.selects import authors, affiliations, subjects, affiliations_authors, authors_subjects
from gui.misc.checkedComboBox import CheckedComboBox
from gui.misc.messageBox import show_message
from misc.filters import filter_authors_by_name


class AuthorFilterWindow(QMainWindow):
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
        main_window.setWindowTitle('Фільтр авторів')
        main_window.resize(530, 240)
        self.centralWidget = QWidget(main_window)

        self.intValidator = QIntValidator()

        self.nameL = QLabel(self.centralWidget)
        self.nameL.setText('Ім`я')
        self.nameTB = QLineEdit(self.centralWidget)

        self.affiliationsL = QLabel(self.centralWidget)
        self.affiliationsL.setText('Організації')
        self.affiliationsCCB = CheckedComboBox(self.centralWidget)
        self.affiliationsCCB.addItems(self.affiliations)

        self.subjectsL = QLabel(self.centralWidget)
        self.subjectsL.setText('Інтереси')
        self.subjectsCCB = CheckedComboBox(self.centralWidget)
        self.subjectsCCB.addItems(self.subjects)

        self.hirshL = QLabel(self.centralWidget)
        self.hirshL.setText('Індекс Хірша')
        self.hirshFromL = QLabel(self.centralWidget)
        self.hirshFromL.setText('Від')
        self.hirshFromTB = QLineEdit(self.centralWidget)
        self.hirshFromTB.setValidator(self.intValidator)
        self.hirshToL = QLabel(self.centralWidget)
        self.hirshToL.setText('До')
        self.hirshToTB = QLineEdit(self.centralWidget)
        self.hirshToTB.setValidator(self.intValidator)

        self.acceptB = QPushButton(self.centralWidget)
        self.acceptB.setText('Фільтрувати')
        self.clearB = QPushButton(self.centralWidget)
        self.clearB.setText('Очистити')

        self.nameL.setGeometry(10, 20, 100, 30)
        self.nameTB.setGeometry(120, 20, 400, 30)
        self.affiliationsL.setGeometry(10, 60, 100, 30)
        self.affiliationsCCB.setGeometry(120, 60, 400, 30)
        self.subjectsL.setGeometry(10, 100, 100, 30)
        self.subjectsCCB.setGeometry(120, 100, 400, 30)
        self.hirshL.setGeometry(10, 140, 100, 30)
        self.hirshFromL.setGeometry(120, 140, 50, 30)
        self.hirshFromTB.setGeometry(160, 140, 100, 30)
        self.hirshToL.setGeometry(290, 140, 50, 30)
        self.hirshToTB.setGeometry(330, 140, 100, 30)

        self.acceptB.setGeometry(140, 190, 100, 30)
        self.clearB.setGeometry(330, 190, 100, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.acceptB.clicked.connect(self.on_acceptB_clicked)
        self.clearB.clicked.connect(self.on_clearB_clicked)

    # endregion
    # region EVENTS
    def on_acceptB_clicked(self):
        try:
            auths = authors()

            if self.hirshFromTB.text() != '':
                auths = auths.where(Author.h_index >= int(self.hirshFromTB.text()))

            if self.hirshToTB.text() != '':
                auths = auths.where(Author.h_index <= int(self.hirshToTB.text()))

            auths = [a for a in auths]

            if self.subjectsCCB.hasSelection():
                selected = self.subjectsCCB.getCheckedIndices()
                objs = [self.sub_obj[i] for i in selected]
                auths = list(dict.fromkeys([a.author for a in authors_subjects() if a.subject in objs
                                            and a.author in auths]))

            if self.affiliationsCCB.hasSelection():
                selected = self.affiliationsCCB.getCheckedIndices()
                objs = [self.aff_objs[i] for i in selected]
                auths = list(dict.fromkeys([a.author for a in affiliations_authors() if a.affiliation in objs
                                            and a.author in auths]))

            name = self.nameTB.text()
            if name != '':
                auths = filter_authors_by_name(auths, name)

            if len(auths) == 0:
                show_message('Не знайдено жодного запису')
            else:
                self.set_model(auths)
        except Exception as err:
            print(err)

    def on_clearB_clicked(self):
        self.clear()
    # endregion

    # region HANDLERS
    def clear(self):
        self.nameTB.clear()
        self.affiliationsCCB.clearSelection()
        self.subjectsCCB.clearSelection()
        self.hirshFromTB.clear()
        self.hirshToTB.clear()
    # endregion
