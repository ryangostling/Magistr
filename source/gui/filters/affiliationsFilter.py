# External
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout

# Internal
from database.biblio.models import Affiliation
from database.biblio.selects import affiliations
from gui.misc.checkedComboBox import CheckedComboBox
from gui.misc.messageBox import show_message
from misc.filters import filter_affiliations_by_name


class AffiliationFilterWindow(QMainWindow):
    # region SETUP
    def __init__(self, set_model):
        super().__init__()
        self.countries = [a.country
                          for a in affiliations().group_by(Affiliation.country).order_by(Affiliation.country)
                          if a.country is not None]
        self.setup_ui(self)
        self.setup_events()
        self.set_model = set_model

        self.clear()

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Фільтр організацій')
        main_window.resize(500, 200)
        self.centralWidget = QWidget(main_window)
        self.gLayout_1 = QGridLayout(self.centralWidget)
        self.gLayout_1.setSpacing(10)

        self.nameL = QLabel(self.centralWidget)
        self.nameL.setText('Назва')
        self.nameTB = QLineEdit(self.centralWidget)

        self.countryL = QLabel(self.centralWidget)
        self.countryL.setText('Країна')
        self.countryCCB = CheckedComboBox(self.centralWidget)
        self.countryCCB.addItems(self.countries)

        self.cityL = QLabel(self.centralWidget)
        self.cityL.setText('Місто')
        self.cityCCB = CheckedComboBox(self.centralWidget)

        self.acceptB = QPushButton(self.centralWidget)
        self.acceptB.setText('Фільтрувати')
        self.clearB = QPushButton(self.centralWidget)
        self.clearB.setText('Очистити')

        self.gLayout_1.addWidget(self.nameL, 0, 0)
        self.gLayout_1.addWidget(self.nameTB, 0, 1, 1, 4)
        self.gLayout_1.addWidget(self.countryL, 1, 0)
        self.gLayout_1.addWidget(self.countryCCB, 1, 1, 1, 4)
        self.gLayout_1.addWidget(self.cityL, 2, 0)
        self.gLayout_1.addWidget(self.cityCCB, 2, 1, 1, 4)
        self.gLayout_1.addWidget(self.acceptB, 3, 1)
        self.gLayout_1.addWidget(self.clearB, 3, 3)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.acceptB.clicked.connect(self.on_acceptB_clicked)
        self.clearB.clicked.connect(self.on_clearB_clicked)
        self.countryCCB.activated.connect(self.on_countryCCB_activated)

    def on_countryCCB_activated(self, value):
        if self.countryCCB.hasSelection():
            self.cityCCB.clearSelection()
            self.cityCCB.clear()
            selected = [i.index().row() for i in self.countryCCB.getChecked()]
            items = [self.countries[i] for i in range(len(self.countries)) if i in selected]
            self.cities = list(dict.fromkeys([a.city for a in affiliations().order_by(Affiliation.city)
                                              if a.country in items]))
            self.cityCCB.addItems(self.cities)

    # endregion
    # region EVENTS
    def on_acceptB_clicked(self):
        affs = affiliations()

        if self.cityCCB.hasSelection():
            selected = [i.index().row() for i in self.cityCCB.getChecked()]
            items = [self.cities[i] for i in range(len(self.cities)) if i in selected]
            affs = [a for a in affiliations() if a.city in items]
        elif self.countryCCB.hasSelection():
            selected = [i.index().row() for i in self.countryCCB.getChecked()]
            items = [self.countries[i] for i in range(len(self.countries)) if i in selected]
            affs = [a for a in affiliations() if a.country in items]

        name = self.nameTB.text()
        if name != '':
            affs = filter_affiliations_by_name(affs, name)

        if len(affs) == 0:
            show_message('Не знайдено жодного запису')
        else:
            self.set_model(affs)

    def on_clearB_clicked(self):
        self.clear()
    # endregion

    # region HANDLERS
    def clear(self):
        self.nameTB.clear()
        self.countryCCB.clearSelection()
        self.cityCCB.clearSelection()
        self.cityCCB.clear()
    # endregion