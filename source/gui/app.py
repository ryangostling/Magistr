# External
import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QWidget, QHeaderView

# Internal
from database.biblio.queries import get_authors_by_pub_id, get_affiliations_by_pub_id, get_subjects_by_publication_id, \
    get_sources, get_affiliations_by_author_id, get_subjects_by_author_id, get_pubs_count_by_author_id, \
    get_authors_count_by_aff_id, get_pubs_count_by_aff_id, get_citations_count
from database.biblio.selects import authors, publications, affiliations
from gui.design import UiMainWindow
from gui.filters.affiliationsFilter import AffiliationFilterWindow
from gui.filters.authorsFilter import AuthorFilterWindow
from gui.filters.publicationsFilter import PublicationFilterWindow
from gui.misc.tableModel import TableModel
from gui.tabs.admin import AdminTab
from gui.tabs.info import InfoTab
from gui.tabs.parser import ParserTab
from gui.tabs.verification import VerifierTab


class AppWindow(QMainWindow, UiMainWindow):
    # region SETUP
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setup_ui(self)
        self.update_db()
        role = self.user.role.role_name

        self.infoTab = InfoTab(self.tab_2, role)
        self.parserTb = ParserTab(self.tab_3, self.update_db)
        self.verifierTab = VerifierTab(self.tab_4, self.update_db, self.openInfoTab)

        print(role)
        if role == 'Admin':
            self.tab_5 = QWidget(self.tabWidget)
            self.tabWidget.addTab(self.tab_5, 'Адміністрування')
            self.adminTab = AdminTab(self.tab_5, self.user)

        self.setup_events()

        self.setModel(self.dbGrid, self.publications)
        self.windows = []


    def setup_events(self):
        self.dbCB.currentTextChanged.connect(self.on_dbCB_changed)
        self.filterB.clicked.connect(self.on_filterB_clicked)
        self.clearB.clicked.connect(self.on_clearB_clicked)
        self.dbGrid.doubleClicked.connect(self.on_dbGrid_doubleClicked)
    # endregion

   # region EVENTS

    def update_db(self):
        self.publications = self.load_pubs(publications())
        self.authors = self.load_authors(authors())
        self.affiliations = self.load_affiliations(affiliations())

    def on_dbCB_changed(self, value):
        try:
            if value == 'Публікації':
                self.setModel(self.dbGrid, self.publications)
            elif value == 'Автори':
                self.setModel(self.dbGrid, self.authors)
            elif value == 'Організації':
                self.setModel(self.dbGrid, self.affiliations)
        except Exception as err:
            print(err)

    def on_filterB_clicked(self):
        value = self.dbCB.currentText()
        filter_window = None
        try:
            if value == 'Публікації':
                filter_window = PublicationFilterWindow(self.fill_pubs)
            elif value == 'Автори':
                filter_window = AuthorFilterWindow(self.fill_authors)
            elif value == 'Організації':
                filter_window = AffiliationFilterWindow(self.fill_affiliations)
            self.windows.append(filter_window)
            filter_window.show()
        except Exception as err:
            print(err)

    def on_clearB_clicked(self):
        value = self.dbCB.currentText()
        if value == 'Публікації':
            self.setModel(self.dbGrid, self.publications)
        elif value == 'Автори':
            self.setModel(self.dbGrid, self.authors)
        elif value == 'Організації':
            self.setModel(self.dbGrid, self.affiliations)

    def on_dbGrid_doubleClicked(self, idx):
        uid = self.dbGrid.model().index(idx.row(), 0).data()
        value = self.dbCB.currentText()
        self.openInfoTab(uid, value)

    # endregion
    # region HANDLERS

    def load_pubs(self, pub_list):
        items_list = []
        for row in pub_list:
            auth_list = get_authors_by_pub_id(row.publication_id)
            aff_list = get_affiliations_by_pub_id(row.publication_id)
            sub_list = get_subjects_by_publication_id(row.publication_id)
            sources = get_sources(row)
            items_list.append(
                [row.publication_id, row.title, row.abstract, row.url, row.cited_by_count, sub_list, row.keywords,
                 row.pub_date, auth_list, aff_list, sources])
        df = pd.DataFrame(items_list,
                          columns=['id', 'Назва', 'Анотація', 'Посилання', 'К-сть цитувань', 'Теми', 'Ключові слова',
                                   'Дата публікації', 'Автори', 'Організації', 'Джерела'])

        return df

    def load_authors(self, auth_list):
        items_list = []
        for row in auth_list:
            aff_list = get_affiliations_by_author_id(row.author_id)
            sub_list = get_subjects_by_author_id(row.author_id)
            count = get_pubs_count_by_author_id(row.author_id)
            cits = get_citations_count(row.author_id)
            items_list.append([row.author_id, row.name, count, row.h_index, cits, row.coauthors_count,
                               aff_list, sub_list])
        df = pd.DataFrame(items_list,
                          columns=['id', 'Ім`я', 'К-сть публікацій', 'Індекс Хірша', 'К-сть цитувань',
                                   'К-сть співавторів', 'Організації', 'Інтереси'])

        return df

    def load_affiliations(self, aff_list):
        items_list = []
        for row in aff_list:
            auths_count = get_authors_count_by_aff_id(row.affiliation_id)
            pubs_count = get_pubs_count_by_aff_id(row.affiliation_id)
            items_list.append(
                [row.affiliation_id, row.affiliation_name, row.city, row.country, row.url, auths_count,
                 pubs_count])
        df = pd.DataFrame(items_list,
                          columns=['id', 'Назва', 'Місто', 'Країна', 'Посилання', 'К-ість авторів',
                                   'К-ість публікацій'])
        return df

    def fill_pubs(self, pub_list):
        df = self.load_pubs(pub_list)
        self.setModel(self.dbGrid, df)

    def fill_authors(self, auth_list):
        df = self.load_authors(auth_list)
        self.setModel(self.dbGrid, df)

    def fill_affiliations(self, aff_list):
        df = self.load_affiliations(aff_list)
        self.setModel(self.dbGrid, df)

    def setModel(self, grid, df):
        model = TableModel(df)
        grid.setModel(model)

        header = grid.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        sizes = []
        for i in range(len(df.columns)):
            sizes.append(header.sectionSize(i))
        header.setSectionResizeMode(QHeaderView.Interactive)
        for i in range(len(df.columns)):
            header.resizeSection(i, sizes[i])

    def openInfoTab(self, uid, value):
        self.tabWidget.setCurrentIndex(1)
        self.infoTab.switch(value, uid)
    # endregion