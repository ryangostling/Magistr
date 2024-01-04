# External
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton

# Internal
from database.accounts.models import User
from database.accounts.selects import users
from gui.app import AppWindow
from gui.misc.messageBox import show_message
from misc.userManager import UserManager


class LoginWidget(QMainWindow):
    # region SETUP
    def __init__(self):
        super().__init__()
        self.userManager = UserManager()

        self.setup_ui(self)
        self.setup_events()
        self.windows = []

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Авторизація')
        main_window.resize(330, 160)
        self.centralWidget = QWidget(main_window)

        self.usernameL = QLabel(self.centralWidget)
        self.usernameL.setText('Логін')
        self.usernameTB = QLineEdit(self.centralWidget)
        self.passwordL = QLabel(self.centralWidget)
        self.passwordL.setText('Пароль')
        self.passwordTB = QLineEdit(self.centralWidget)

        self.signInB = QPushButton(self.centralWidget)
        self.signInB.setText('Вхід')

        self.usernameL.setGeometry(10, 20, 100, 30)
        self.usernameTB.setGeometry(70, 20, 250, 30)
        self.usernameTB.setText('nekhaienkoihortr82@gmail.com')
        self.passwordL.setGeometry(10, 60, 100, 30)
        self.passwordTB.setGeometry(70, 60, 250, 30)
        self.passwordTB.setText('1488')

        self.signInB.setGeometry(70, 110, 200, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.signInB.clicked.connect(self.on_signInB_clicked)
    # endregion

    # region EVENTS
    def on_signInB_clicked(self):
        try:
            username = self.usernameTB.text()
            password = self.passwordTB.text()

            if username == '' or password == '':
                return

            if any(users().where(User.username == username)):
                user = users().where(User.username == username).get()
                if self.userManager.validate(user, password):
                    self.hide()
                    aw = AppWindow(user)
                    self.windows.append(aw)
                    aw.show()
                else:
                    show_message('Невірний пароль')
                    return
            else:
                show_message('Невірний логін')
        except Exception as err:
            print(err)


    # endregion

    # region HANDLERS

    # endregion
