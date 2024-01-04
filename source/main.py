# External
from PyQt5.QtWidgets import QApplication
import sys

# Internal
from database.accounts.context import db as acc_db
from database.accounts.models import *
from database.accounts.selects import users
from database.biblio.context import db as bib_db
from database.biblio.models import *
from gui.authorizing.login import LoginWidget
from misc.userManager import UserManager


# Створення таблиць БД
def create_tables():
    try:
        Role.create_table()
        User.create_table()
        Affiliation.create_table()
        Author.create_table()
        Subject.create_table()
        AuthorSubject.create_table()
        Publication.create_table()
        PublicationSubject.create_table()
        AuthorPublication.create_table()
        AffiliationPublication.create_table()
        AffiliationAuthor.create_table()

        if not any(users().where(User.user_id == 1)):
            admin = Role.create(role_name='Admin')
            Role.create(role_name='User')
            um = UserManager()
            User.create(username='nekhaienkoihortr82@gmail.com', name='Ihor Nekhaienko',
                        password=um.get_hash('1488'), role=admin)
    except Exception as err:
        print(err)

# Завантаження інтерфейсу
def load_gui():
    app = QApplication(sys.argv)
    aw = LoginWidget()
    aw.show()
    sys.exit(app.exec())

def main():
    try:
        # Підключення до БД
        bib_db.connect()
        acc_db.connect()
        create_tables()

        load_gui()
    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
