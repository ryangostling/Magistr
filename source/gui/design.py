# External
from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QComboBox, QTableView, QPushButton, QGridLayout


class UiMainWindow(object):
    def setup_ui(self, main_window):
        main_window.setObjectName("MainWindow")
        main_window.setWindowTitle('Система верифікації')
        main_window.resize(1920, 1080)
        self.centralWidget = QWidget(main_window)
        self.vLayout = QVBoxLayout(self.centralWidget)
        self.tabWidget = QTabWidget(self.centralWidget)

        self.tab_1 = QWidget(self.tabWidget)
        # region TAB 1
        self.intValidator = QIntValidator()
        self.dbCB = QComboBox(self.tab_1)
        self.dbCB.addItem("Публікації")
        self.dbCB.addItem("Автори")
        self.dbCB.addItem("Організації")
        self.dbGrid = QTableView(self.tab_1)
        self.dbGrid.setSortingEnabled(True)
        self.filterB = QPushButton(self.tab_1)
        self.filterB.setText("Фільтр")
        self.clearB = QPushButton(self.tab_1)
        self.clearB.setText("Очистити фільтр")
        self.gLayout_1 = QGridLayout(self.tab_1)
        self.gLayout_1.setSpacing(10)
        self.gLayout_1.addWidget(self.dbCB, 0, 0)
        self.gLayout_1.addWidget(self.dbGrid, 1, 0, 5, 10)
        self.gLayout_1.addWidget(self.filterB, 0, 1)
        self.gLayout_1.addWidget(self.clearB, 0, 2)

        self.tab_2 = QWidget(self.tabWidget)
        self.tab_3 = QWidget(self.tabWidget)
        self.tab_4 = QWidget(self.tabWidget)

        # endregion

        self.tabWidget.addTab(self.tab_1, 'База даних')
        self.tabWidget.addTab(self.tab_2, 'Детальна інформація')
        self.tabWidget.addTab(self.tab_3, 'Завантаження інформації')
        self.tabWidget.addTab(self.tab_4, 'Верифікація')

        self.vLayout.addWidget(self.tabWidget)
        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)
        self.showMaximized()
