# External
from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton

# Internal
from database.biblio.context import db
from database.biblio.models import Affiliation
from database.biblio.selects import affiliations
from gui.misc.messageBox import show_message


class AffiliationCreator(QMainWindow):
    # region SETUP
    def __init__(self, filler):
        super().__init__()
        self.filler = filler

        self.setup_ui(self)
        self.setup_events()

        self.clear()

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Конструктор організацій')
        main_window.resize(500, 240)
        self.centralWidget = QWidget(main_window)
        self.intValidator = QIntValidator()

        self.affNameL = QLabel(self.centralWidget)
        self.affNameL.setText('Назва')
        self.affNameTB = QLineEdit(self.centralWidget)
        self.countryL = QLabel(self.centralWidget)
        self.countryL.setText('Країна')
        self.countryTB = QLineEdit(self.centralWidget)
        self.cityL = QLabel(self.centralWidget)
        self.cityL.setText('Місто')
        self.cityTB = QLineEdit(self.centralWidget)
        self.addressL = QLabel(self.centralWidget)
        self.addressL.setText('Адреса')
        self.addressTB = QLineEdit(self.centralWidget)
        self.urlL = QLabel(self.centralWidget)
        self.urlL.setText('Посилання')
        self.urlTB = QLineEdit(self.centralWidget)

        self.createB = QPushButton(self.centralWidget)
        self.createB.setText('Додати')

        self.affNameL.setGeometry(10, 20, 100, 30)
        self.affNameTB.setGeometry(120, 20, 370, 30)
        self.countryL.setGeometry(10, 60, 100, 30)
        self.countryTB.setGeometry(120, 60, 150, 30)
        self.cityL.setGeometry(280, 60, 50, 30)
        self.cityTB.setGeometry(340, 60, 150, 30)
        self.addressL.setGeometry(10, 100, 100, 30)
        self.addressTB.setGeometry(120, 100, 370, 30)
        self.urlL.setGeometry(10, 140, 100, 30)
        self.urlTB.setGeometry(120, 140, 370, 30)

        self.createB.setGeometry(160, 190, 200, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.createB.clicked.connect(self.on_createB_clicked)
    # endregion

    # region EVENTS
    def on_createB_clicked(self):
        try:
            if self.affNameTB.text() == '':
                return
            with db.atomic():
                if len(affiliations()) != 0:
                    uid = affiliations().order_by(Affiliation.affiliation_id.desc()) \
                              .get().affiliation_id + 1
                else:
                    uid = 1
                affiliation_name = self.affNameTB.text()

                if any(affiliations().where(Affiliation.affiliation_name == affiliation_name)):
                    show_message('Організація з такою назвою вже існує')
                    return

                country = self.countryTB.text()
                city = self.cityTB.text()
                address = self.addressTB.text()
                url = self.urlTB.text()
                Affiliation.create(affiliation_id=uid, affiliation_name=affiliation_name, country=country, city=city,
                                   address=address, url=url)

                self.filler(uid)
                self.close()
        except Exception as err:
            print(err)
    # endregion

    # region HANDLERS
    def clear(self):
        self.affNameTB.clear()
        self.countryTB.clear()
        self.cityTB.clear()
        self.addressTB.clear()
        self.urlTB.clear()
    # endregion
