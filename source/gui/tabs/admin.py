# External
import pandas as pd
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QCheckBox, QTableView, QHeaderView

# Internal
from database.accounts.models import Role, User
from database.accounts.selects import roles, users
from gui.authorizing.changePassword import ChangePasswordWidget
from gui.misc.tableModel import TableModel
from misc.emailService import EmailService
from misc.userManager import UserManager


class AdminTab:
    # region SETUP

    def __init__(self, page, admin):
        self.page = page
        self.admin = admin
        self.admin_role = roles().where(Role.role_name == 'Admin').get()
        self.user_role = roles().where(Role.role_name == 'User').get()

        self.setup_ui()
        self.setup_events()

        self.fill_users()

        self.userManager = UserManager()
        self.emailService = EmailService()
        self.windows = []

        self.clear()

    def setup_ui(self):
        self.nameL = QLabel(self.page)
        self.nameL.setText("Ім'я")
        self.nameTB = QLineEdit(self.page)
        self.usernameL = QLabel(self.page)
        self.usernameL.setText('Логін')
        self.usernameTB = QLineEdit(self.page)
        self.passwordL = QLabel(self.page)
        self.passwordL.setText('Пароль')
        self.passwordTB = QLineEdit(self.page)
        self.randomI = QPushButton(self.page)
        self.randomI.setStyleSheet("background-image : url(resources/dice.png);")
        self.isAdminChB = QCheckBox(self.page)
        self.isAdminChB.setText('Адмін')

        self.addEditB = QPushButton(self.page)
        self.addEditB.setText('Додати')
        self.clearB = QPushButton(self.page)
        self.clearB.setText('Очистити')
        self.deleteB = QPushButton(self.page)
        self.deleteB.setText('Видалити')
        self.passwordB = QPushButton(self.page)
        self.passwordB.setText('Відновити пароль')

        self.adminGrid = QTableView(self.page)
        self.adminGrid.setSortingEnabled(True)

        self.nameL.setGeometry(10, 20, 100, 30)
        self.nameTB.setGeometry(70, 20, 200, 30)
        self.usernameL.setGeometry(10, 60, 100, 30)
        self.usernameTB.setGeometry(70, 60, 200, 30)
        self.passwordL.setGeometry(280, 60, 100, 30)
        self.passwordTB.setGeometry(340, 60, 200, 30)
        self.randomI.setGeometry(550, 60, 35, 32)
        self.isAdminChB.setGeometry(10, 100, 100, 30)

        self.addEditB.setGeometry(10, 150, 100, 30)
        self.clearB.setGeometry(120, 150, 100, 30)
        self.deleteB.setGeometry(230, 150, 100, 30)
        self.passwordB.setGeometry(340, 150, 150, 30)
        self.adminGrid.setGeometry(10, 200, 1870, 780)

    def setup_events(self):
        self.addEditB.clicked.connect(self.on_addEditB_clicked)
        self.clearB.clicked.connect(self.on_clearB_clicked)
        self.deleteB.clicked.connect(self.on_deleteB_clicked)
        self.randomI.clicked.connect(self.on_randomI_clicked)
        self.passwordB.clicked.connect(self.on_passwordB_clicked)
        self.adminGrid.clicked.connect(self.on_adminGrid_clicked)

    # endregion

    # region EVENTS
    def on_addEditB_clicked(self):
        if self.addEditB.text() == 'Додати':
            self.add()
        else:
            self.edit()

    def on_clearB_clicked(self):
        self.clear()

    def on_deleteB_clicked(self):
        try:
            if self.current is None:
                return

            self.emailService.notify_delete(self.current.username)
            self.current.delete_instance()
            self.fill_users()
            self.clear()
        except Exception as err:
            print(err)

    def on_randomI_clicked(self):
        try:
            self.password = self.userManager.randomize_password()
            self.hashPassword = self.userManager.get_hash(self.password)
            print(self.password)
            self.passwordTB.setText(''.join(['*' for _ in range(len(self.password))]))
        except Exception as err:
            print(err)

    def on_adminGrid_clicked(self, idx):
        uid = self.adminGrid.model().index(idx.row(), 0).data()
        self.current = users().where(User.user_id == uid).get()

        self.nameTB.setText(self.current.name)
        self.usernameTB.setText(self.current.username)
        self.passwordTB.setText(''.join(['*' for _ in range(len(self.current.password))]))

        self.addEditB.setText('Редагувати')

        if self.current.role == self.admin_role:
            self.isAdminChB.setChecked(True)
        else:
            self.isAdminChB.setChecked(False)

        if self.current == self.admin:
            self.passwordB.setText('Змінити пароль')
        else:
            self.passwordB.setText('Відновити пароль')

        self.passwordB.show()

        self.password = None
        self.randomI.setEnabled(False)

        if self.current == self.admin or self.current.user_id == 1:
            self.deleteB.setEnabled(False)
        else:
            self.deleteB.setEnabled(True)

        if self.current.role == self.user_role or (self.admin.user_id == 1 and self.current != self.admin):
            self.isAdminChB.setEnabled(True)
        else:
            self.isAdminChB.setEnabled(False)

    def on_passwordB_clicked(self):
        try:
            if self.passwordB.text() == 'Змінити пароль':
                cp = ChangePasswordWidget(self.current, self.userManager)
                cp.show()
                self.windows.append(cp)
            else:
                password = self.userManager.randomize_password()
                self.current.password = self.userManager.get_hash(password)
                self.current.save()
                self.emailService.notify_restore(self.current.username, password, self.current.username)
        except Exception as err:
            print(err)
    # endregion

    # region HANDLERS

    def add(self):
        try:
            name = self.nameTB.text()
            username = self.usernameTB.text()
            password = self.password if self.password is not None else self.passwordTB.text()

            if name == '' or username == '' or password == '' or not self.userManager.is_email_valid(username) \
                    or any(users().where(User.username == username)):
                return

            if self.isAdminChB.isChecked():
                role = self.admin_role
            else:
                role = self.user_role

            User.create(name=name, username=username, password=self.userManager.get_hash(password), role=role)
            self.emailService.notify_add(username, password, username)
            self.fill_users()
            self.clear()
        except Exception as err:
            print(err)

    def edit(self):
        try:
            name = self.nameTB.text()
            username = self.usernameTB.text()

            if name == '' or username == '' or not self.userManager.is_email_valid(username):
                return

            if self.isAdminChB.isChecked():
                role = self.admin_role
            else:
                role = self.user_role

            self.current.name = name
            self.current.username = username
            self.current.role = role
            self.current.save()

            self.fill_users()
            self.clear()
        except Exception as err:
            print(err)

    def fill_users(self):
        items_list = []
        for row in users():
            items_list.append([row.user_id, row.name, row.username, row.password])
        df = pd.DataFrame(items_list,
                          columns=['id', 'Ім`я', 'Логін', 'Пароль'])
        self.setModel(self.adminGrid, df)

    def setModel(self, grid, df):
        model = TableModel(df)
        grid.setModel(model)
        header = grid.horizontalHeader()
        sizes = [30, 300, 300, 300]
        header.setSectionResizeMode(QHeaderView.Interactive)
        for i in range(len(df.columns)):
            header.resizeSection(i, sizes[i])

    def clear(self):
        self.password = None
        self.current = None
        self.nameTB.clear()
        self.usernameTB.clear()
        self.passwordTB.clear()
        self.isAdminChB.setChecked(False)
        self.randomI.setEnabled(True)
        self.deleteB.setEnabled(True)
        self.isAdminChB.setEnabled(True)
        self.addEditB.setText('Додати')
        self.passwordB.hide()
    # endregion
