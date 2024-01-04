# External
from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton

# Internal
from database.biblio.models import Affiliation
from database.biblio.selects import affiliations


class AffiliationEditor(QMainWindow):
    # region SETUP
    def __init__(self, uid, filler):
        super().__init__()
        self.affiliation = affiliations().where(Affiliation.affiliation_id == uid).get()
        self.filler = filler

        self.setup_ui(self)
        self.setup_events()

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Редактор організацій')
        main_window.resize(500, 280)
        self.centralWidget = QWidget(main_window)
        self.intValidator = QIntValidator()

        self.idL = QLabel(self.centralWidget)
        self.idL.setText('id')
        self.idTB = QLineEdit(self.centralWidget)
        self.idTB.setText(str(self.affiliation.affiliation_id))
        self.idTB.setEnabled(False)
        self.affNameL = QLabel(self.centralWidget)
        self.affNameL.setText('Назва')
        self.affNameTB = QLineEdit(self.centralWidget)
        self.affNameTB.setText(str(self.affiliation.affiliation_name))
        self.countryL = QLabel(self.centralWidget)
        self.countryL.setText('Країна')
        self.countryTB = QLineEdit(self.centralWidget)
        self.countryTB.setText(str(self.affiliation.country))
        self.cityL = QLabel(self.centralWidget)
        self.cityL.setText('Місто')
        self.cityTB = QLineEdit(self.centralWidget)
        self.cityTB.setText(str(self.affiliation.city))
        self.addressL = QLabel(self.centralWidget)
        self.addressL.setText('Адреса')
        self.addressTB = QLineEdit(self.centralWidget)
        self.addressTB.setText(str(self.affiliation.address))
        self.urlL = QLabel(self.centralWidget)
        self.urlL.setText('Посилання')
        self.urlTB = QLineEdit(self.centralWidget)
        self.urlTB.setText(str(self.affiliation.url))

        self.updateB = QPushButton(self.centralWidget)
        self.updateB.setText('Зберегти')

        self.idL.setGeometry(10, 20, 100, 30)
        self.idTB.setGeometry(120, 20, 100, 30)
        self.affNameL.setGeometry(10, 60, 100, 30)
        self.affNameTB.setGeometry(120, 60, 370, 30)
        self.countryL.setGeometry(10, 100, 100, 30)
        self.countryTB.setGeometry(120, 100, 150, 30)
        self.cityL.setGeometry(280, 100, 50, 30)
        self.cityTB.setGeometry(340, 100, 150, 30)
        self.addressL.setGeometry(10, 140, 100, 30)
        self.addressTB.setGeometry(120, 140, 370, 30)
        self.urlL.setGeometry(10, 180, 100, 30)
        self.urlTB.setGeometry(120, 180, 370, 30)

        self.updateB.setGeometry(160, 230, 200, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)


    def setup_events(self):
        self.updateB.clicked.connect(self.on_updateB_clicked)
    # endregion

    # region EVENTS
    def on_updateB_clicked(self):
        if self.affNameTB.text() == '':
            return
        self.affiliation.affiliation_name = self.affNameTB.text()

        self.affiliation.country = self.countryTB.text()
        self.affiliation.city = self.cityTB.text()
        self.affiliation.address = self.addressTB.text()
        self.affiliation.url = self.urlTB.text()
        self.affiliation.save()

        self.filler(self.affiliation.affiliation_id)

        self.close()
    # endregion
