# External
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPushButton

# Internal
from gui.misc.messageBox import show_message


class ChangePasswordWidget(QMainWindow):
    # region SETUP
    def __init__(self, user, userManager):
        super().__init__()
        self.user = user
        self.userManager = userManager

        self.setup_ui(self)
        self.setup_events()

    def setup_ui(self, main_window):
        main_window.setWindowTitle('Зміна паролю')
        main_window.resize(380, 200)
        self.centralWidget = QWidget(main_window)

        self.oldPasswordL = QLabel(self.centralWidget)
        self.oldPasswordL.setText('Старий пароль')
        self.oldPasswordTB = QLineEdit(self.centralWidget)
        self.newPasswordL1 = QLabel(self.centralWidget)
        self.newPasswordL1.setText('Новий пароль')
        self.newPasswordTB1 = QLineEdit(self.centralWidget)
        self.newPasswordL2 = QLabel(self.centralWidget)
        self.newPasswordL2.setText('Підтвердити')
        self.newPasswordTB2 = QLineEdit(self.centralWidget)

        self.changePasswordB = QPushButton(self.centralWidget)
        self.changePasswordB.setText('Змінити пароль')

        self.oldPasswordL.setGeometry(10, 20, 100, 30)
        self.oldPasswordTB.setGeometry(120, 20, 250, 30)
        self.newPasswordL1.setGeometry(10, 60, 150, 30)
        self.newPasswordTB1.setGeometry(120, 60, 250, 30)
        self.newPasswordL2.setGeometry(10, 100, 150, 30)
        self.newPasswordTB2.setGeometry(120, 100, 250, 30)

        self.changePasswordB.setGeometry(90, 150, 200, 30)

        main_window.setCentralWidget(self.centralWidget)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def setup_events(self):
        self.changePasswordB.clicked.connect(self.on_changePasswordB_clicked)
    # endregion

    # region EVENTS
    def on_changePasswordB_clicked(self):
        try:
            old = self.oldPasswordTB.text()
            new1 = self.newPasswordTB1.text()
            new2 = self.newPasswordTB2.text()

            if old == '' or new1 == '' or new2 == '':
                return

            if new1 != new2:
                show_message('Паролі мають зівпадати')
                return

            if self.userManager.validate(self.user, old):
                self.user.password = self.userManager.get_hash(new1)
                self.user.save()
                self.close()
            else:
                show_message('Невірний старий пароль')
                return
        except Exception as err:
            print(err)
    # endregion

    # region HANDLERS

    # endregion
