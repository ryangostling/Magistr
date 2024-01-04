# External
from collections import Counter
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIntValidator, QDesktopServices
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QTableView, QHeaderView, QComboBox, QWidget, QVBoxLayout

# Internal
from database.biblio.context import db
from database.biblio.models import Affiliation, AffiliationAuthor, Author, AuthorPublication, Publication, \
    PublicationSubject, AffiliationPublication, AuthorSubject
from database.biblio.queries import get_authors_by_pub_id, get_affiliations_by_pub_id, get_subjects_by_publication_id, \
    get_sources, get_subjects_by_author_id, get_affiliations_by_author_id, get_pubs_count_by_author_id, \
    get_authors_count_by_aff_id, get_pubs_count_by_aff_id, get_abbs_by_publication_id, get_citations_count
from database.biblio.selects import affiliations, subjects, authors, publications
from gui.creators.affiliationCreator import AffiliationCreator
from gui.creators.authorCreator import AuthorCreator
from gui.creators.publicationCreator import PublicationCreator
from gui.editors.affiliationEditor import AffiliationEditor
from gui.editors.authorEditor import AuthorEditor
from gui.editors.publicationEditor import PublicationEditor
from gui.misc.charts import create_bar_chart, create_graph_chart, create_pie_chart
from gui.misc.tableModel import TableModel


class InfoTab:
    # region SETUP
    def __init__(self, page, role):
        self.page = page
        self.setup_ui()
        self.setup_events()

        self.role = role
        self.hide_pub()
        self.hide_author()
        self.hide_aff()
        self.deleteB.hide()
        if self.role == 'User':
            self.addEditB.hide()
            self.clearB.hide()

        self.addEditB.setText('Додати')
        self.windows = []

    def setup_ui(self):
        self.intValidator = QIntValidator()
        self.boldFont = QtGui.QFont()
        self.boldFont.setBold(True)

        self.infoCB = QComboBox(self.page)
        self.infoCB.addItems(['Публікація', 'Автор', 'Організація'])
        self.infoCB.setCurrentIndex(0)
        self.idL = QLabel(self.page)
        self.idL.setText('id')
        self.idL.setFont(self.boldFont)
        self.idTB = QLineEdit(self.page)
        self.idTB.setValidator(self.intValidator)
        self.retrieveB = QPushButton(self.page)
        self.retrieveB.setText('Знайти')
        self.clearB = QPushButton(self.page)
        self.clearB.setText('Очистити')
        self.addEditB = QPushButton(self.page)
        self.addEditB.setText('Додати')
        self.deleteB = QPushButton(self.page)
        self.deleteB.setText('Видалити')

        self.infoCB.setGeometry(10, 10, 100, 30)
        self.idL.setGeometry(10, 50, 20, 30)
        self.idTB.setGeometry(40, 50, 50, 30)
        self.retrieveB.setGeometry(100, 50, 100, 30)

        self.clearB.setGeometry(1560, 50, 100, 30)
        self.addEditB.setGeometry(1670, 50, 100, 30)
        self.deleteB.setGeometry(1780, 50, 100, 30)

        # region PUBLICATION
        self.pTitleTBL = QLabel(self.page)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.pTitleTBL.setFont(font)
        self.pDateTBL = QLabel(self.page)
        self.pCitTBL = QLabel(self.page)
        self.pLinkTBL = QLabel(self.page)
        self.pAbstractL = QLabel(self.page)
        self.pAbstractL.setText('Короткий опис')
        font.setPointSize(10)
        self.pAbstractL.setFont(font)

        self.pAbstractLRTB = QLabel(self.page)
        self.pAbstractLRTB.setAlignment(Qt.AlignTop)
        self.pAbstractLRTB.setWordWrap(True)

        self.pubCB = QComboBox(self.page)
        self.pubCB.addItems(['Автори', 'Організації', 'Теми'])
        self.pubCB.setCurrentIndex(0)
        self.pubGrid = QTableView(self.page)
        self.pubGrid.setSortingEnabled(True)

        self.pTitleTBL.setGeometry(10, 90, 1870, 40)
        self.pDateTBL.setGeometry(10, 140, 80, 30)
        self.pCitTBL.setGeometry(100, 140, 100, 30)
        self.pLinkTBL.setGeometry(10, 170, 130, 30)
        self.pAbstractL.setGeometry(430, 200, 200, 30)
        self.pAbstractLRTB.setGeometry(10, 230, 1000, 260)

        self.pubCB.setGeometry(10, 510, 100, 30)
        self.pubGrid.setGeometry(10, 550, 1870, 390)
        # endregion

        # region AUTHOR
        self.authorL = QLabel(self.page)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.authorL.setFont(font)
        self.aOverviewL = QLabel(self.page)
        self.aOverviewL.setText('Огляд показників')
        font.setPointSize(10)
        self.aOverviewL.setFont(font)
        self.aTrendL = QLabel(self.page)
        self.aTrendL.setText('Огляд тенденцій')
        self.aTrendL.setFont(font)
        self.aDocsTBL = QLabel(self.page)
        self.aDocsL = QLabel(self.page)
        self.aDocsL.setText('Документів')
        self.aDocsL.setFont(self.boldFont)
        self.aCitsCBL = QLabel(self.page)
        self.aCitsL = QLabel(self.page)
        self.aCitsL.setText('Цитувань')
        self.aCitsL.setFont(self.boldFont)
        self.aHirshTBL = QLabel(self.page)
        self.aHirshL = QLabel(self.page)
        self.aHirshL.setText('Індекс Хірша')
        self.aHirshL.setFont(self.boldFont)
        self.authorCB = QComboBox(self.page)
        self.authorCB.addItems(['Організації', 'Публікації', 'Теми'])
        self.authorCB.setCurrentIndex(0)
        self.authorGrid = QTableView(self.page)
        self.authorGrid.setSortingEnabled(True)

        self.aCountWidget = QWidget(self.page)
        self.aCountFig = plt.figure()
        self.aCountCanvas = FigureCanvas(self.aCountFig)
        self.aCountToolbar = NavigationToolbar(self.aCountCanvas, self.page)
        self.vLayout_1 = QVBoxLayout(self.aCountWidget)
        self.vLayout_1.addWidget(self.aCountToolbar)
        self.vLayout_1.addWidget(self.aCountCanvas)
        self.aCountWidget.setLayout(self.vLayout_1)

        self.aCitWidget = QWidget(self.page)
        self.aCitFig = plt.figure()
        self.aCitCanvas = FigureCanvas(self.aCitFig)
        self.aCitToolbar = NavigationToolbar(self.aCitCanvas, self.page)
        self.vLayout_2 = QVBoxLayout(self.aCitWidget)
        self.vLayout_2.addWidget(self.aCitToolbar)
        self.vLayout_2.addWidget(self.aCitCanvas)
        self.aCitWidget.setLayout(self.vLayout_2)

        self.authorL.setGeometry(10, 90, 500, 40)
        self.aOverviewL.setGeometry(10, 140, 200, 30)
        self.aTrendL.setGeometry(890, 140, 200, 30)
        self.aCountWidget.setGeometry(220, 170, 745, 380)
        self.aCitWidget.setGeometry(1075, 170, 745, 380)
        self.aDocsTBL.setGeometry(50, 220, 100, 30)
        self.aDocsL.setGeometry(40, 240, 100, 30)
        self.aCitsCBL.setGeometry(50, 260, 100, 30)
        self.aCitsL.setGeometry(40, 280, 100, 30)
        self.aHirshTBL.setGeometry(50, 300, 100, 30)
        self.aHirshL.setGeometry(40, 320, 100, 30)

        self.authorCB.setGeometry(10, 510, 100, 30)
        self.authorGrid.setGeometry(10, 550, 1870, 390)
        # endregion

        # region AFFILIATION
        self.oNameTBL = QLabel(self.page)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.oNameTBL.setFont(font)
        self.oLocationTBL = QLabel(self.page)
        self.oAddressTBL = QLabel(self.page)
        self.oLinkTBL = QLabel(self.page)

        self.oTopicL = QLabel(self.page)
        self.oTopicL.setText('Теми')
        self.oTopicL.setFont(font)

        self.oTopWidget = QWidget(self.page)
        self.oTopFig = plt.figure()
        self.oTopCanvas = FigureCanvas(self.oTopFig)
        self.oTopToolbar = NavigationToolbar(self.oTopCanvas, self.page)
        self.vLayout_2 = QVBoxLayout(self.oTopWidget)
        self.vLayout_2.addWidget(self.oTopToolbar)
        self.vLayout_2.addWidget(self.oTopCanvas)
        self.oTopWidget.setLayout(self.vLayout_2)

        self.affCB = QComboBox(self.page)
        self.affCB.addItems(['Автори', 'Публікації'])
        self.affCB.setCurrentIndex(1)
        self.affGrid = QTableView(self.page)
        self.affGrid.setSortingEnabled(True)

        self.oNameTBL.setGeometry(10, 90, 1000, 40)
        self.oLocationTBL.setGeometry(10, 140, 1000, 30)
        self.oAddressTBL.setGeometry(10, 170, 1000, 30)
        self.oLinkTBL.setGeometry(10, 200, 130, 30)

        self.oTopicL.setGeometry(1050, 140, 50, 30)
        self.oTopWidget.setGeometry(900, 170, 370, 380)

        self.affCB.setGeometry(10, 510, 100, 30)
        self.affGrid.setGeometry(10, 550, 1870, 390)
        # endregion

    def setup_events(self):
        self.retrieveB.clicked.connect(self.on_retrieveB_clicked)
        self.authorCB.currentTextChanged.connect(self.on_authorCB_changed)
        self.pubCB.currentTextChanged.connect(self.on_pubCB_changed)
        self.affCB.currentTextChanged.connect(self.on_affCB_changed)
        self.pubGrid.doubleClicked.connect(self.on_pubGrid_doubleClicked)
        self.authorGrid.doubleClicked.connect(self.on_authorGrid_doubleClicked)
        self.affGrid.doubleClicked.connect(self.on_affGrid_doubleClicked)

        self.addEditB.clicked.connect(self.on_addEditB_clicked)
        self.clearB.clicked.connect(self.on_clearB_clicked)
        self.deleteB.clicked.connect(self.on_deleteB_clicked)
    # endregion
    # region EVENTS
    # region SHARED

    def on_retrieveB_clicked(self):
        value = self.infoCB.currentText()
        uid = self.idTB.text()
        try:
            if uid != '':
                uid = int(uid)
                if value == 'Публікація':
                    if any(publications().where(Publication.publication_id == uid)):
                        self.load_publication(uid)
                        self.infoCB.setCurrentIndex(0)
                elif value == 'Автор':
                    if any(authors().where(Author.author_id == uid)):
                        self.load_author(uid)
                        self.infoCB.setCurrentIndex(1)
                elif value == 'Організація':
                    if any(affiliations().where(Affiliation.affiliation_id == uid)):
                        self.load_affiliation(uid)
                        self.infoCB.setCurrentIndex(2)
                if self.role == 'Admin':
                    self.deleteB.show()
                self.addEditB.setText('Редагувати')
        except Exception as err:
            print(err)

    def on_addEditB_clicked(self):
        try:
            value = self.infoCB.currentText()

            if self.addEditB.text() == 'Додати':
                self.add(value)
            else:
                uid = self.idTB.text()
                if uid == '':
                    return
                self.update(uid, value)
        except Exception as err:
            print(err)

    def on_clearB_clicked(self):
        try:
            self.addEditB.setText('Додати')
            self.idTB.setText('')
            self.hide_pub()
            self.hide_author()
            self.hide_aff()
            self.deleteB.hide()
        except Exception as err:
            print(err)

    def on_deleteB_clicked(self):
        try:
            uid = self.idTB.text()
            value = self.infoCB.currentText()
            if uid == '':
                return
            if value == 'Публікація':
                if any(publications().where(Publication.publication_id == uid)):
                    self.delete_pub(uid)
            elif value == 'Автор':
                if any(authors().where(Author.author_id == uid)):
                    self.delete_author(uid)
            elif value == 'Організація':
                if any(affiliations().where(Affiliation.affiliation_id == uid)):
                    self.delete_aff(uid)

        except Exception as err:
            print(err)

    # endregion

    # region AUTHOR

    def on_authorGrid_doubleClicked(self, idx):
        uid = self.authorGrid.model().index(idx.row(), 0).data()
        value = self.authorCB.currentText()
        try:
            self.idTB.setText(str(uid))
            if value == 'Публікації':
                self.load_publication(uid)
                self.infoCB.setCurrentIndex(0)
            elif value == 'Організації':
                self.load_affiliation(uid)
                self.infoCB.setCurrentIndex(2)
        except Exception as err:
            print(err)

    def on_authorCB_changed(self, value):
        try:
            if value == 'Публікації':
                self.fill_author_publications(self.aPubs)
            elif value == 'Теми':
                self.fill_author_subjects(self.aSubs)
            elif value == 'Організації':
                self.fill_author_affiliations(self.aAffs)
        except Exception as err:
            print(err)
    # endregion

    # region PUBLICATION
    def on_pubGrid_doubleClicked(self, idx):
        uid = self.pubGrid.model().index(idx.row(), 0).data()
        value = self.pubCB.currentText()
        try:
            self.idTB.setText(str(uid))
            if value == 'Автори':
                self.load_author(uid)
                self.infoCB.setCurrentIndex(1)
            elif value == 'Організації':
                self.load_affiliation(uid)
                self.infoCB.setCurrentIndex(2)
        except Exception as err:
            print(err)

    def on_pubCB_changed(self, value):
        try:
            if value == 'Автори':
                self.fill_pub_authors(self.pAuths)
            elif value == 'Організації':
                self.fill_pub_affiliations(self.pAffs)
            elif value == 'Теми':
                self.fill_pub_subjects(self.pSubs)
        except Exception as err:
            print(err)

    # endregion

    # region AFFILIATION
    def on_affGrid_doubleClicked(self, idx):
        uid = self.affGrid.model().index(idx.row(), 0).data()
        value = self.affCB.currentText()
        try:
            self.idTB.setText(str(uid))
            if value == 'Автори':
                self.load_author(uid)
                self.infoCB.setCurrentIndex(1)
            elif value == 'Публікації':
                self.load_publication(uid)
                self.infoCB.setCurrentIndex(0)
        except Exception as err:
            print(err)

    def on_affCB_changed(self, value):
        try:
            if value == 'Автори':
                self.fill_aff_authors(self.oAuthors)
            elif value == 'Публікації':
                self.fill_aff_publications(self.oPubs)
        except Exception as err:
            print(err)
    # endregion
    # endregion

    # region HANDLERS
    # region SHARED
    def add(self, value):
        try:
            if value == 'Публікація':
                create_window = PublicationCreator(self.load_publication)
            elif value == 'Автор':
                create_window = AuthorCreator(self.load_author)
            elif value == 'Організація':
                create_window = AffiliationCreator(self.load_affiliation)
            self.windows.append(create_window)
            create_window.show()
        except Exception as err:
            print(err)

    def update(self, uid, value):
        try:
            if value == 'Публікація':
                if any(publications().where(Publication.publication_id == uid)):
                    update_window = PublicationEditor(uid, self.load_publication)
            elif value == 'Автор':
                if any(authors().where(Author.author_id == uid)):
                    update_window = AuthorEditor(uid, self.load_author)
            elif value == 'Організація':
                if any(affiliations().where(Affiliation.affiliation_id == uid)):
                    update_window = AffiliationEditor(uid, self.load_affiliation)
            self.windows.append(update_window)
            update_window.show()
        except Exception as err:
            print(err)

    def switch(self, value, uid):
        try:
            self.idTB.setText(str(uid))
            if value == 'Публікації':
                self.load_publication(uid)
                self.infoCB.setCurrentIndex(0)
            elif value == 'Автори':
                self.load_author(uid)
                self.infoCB.setCurrentIndex(1)
            elif value == 'Організації':
                self.load_affiliation(uid)
                self.infoCB.setCurrentIndex(2)
            self.addEditB.setText('Редагувати')
            if self.role == 'Admin':
                self.deleteB.show()
        except Exception as err:
            print(err)

    def sql_count(self, l):
        dick = dict()
        for i in l:
            if i[1] in dick:
                dick[i[1]] += i[0]
            else:
                dick[i[1]] = i[0]
        return list(dick.values())

    def open_link(self, link):
        QDesktopServices.openUrl(QUrl(link))

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
    # endregion
    # region PUBLICATION

    def load_publication(self, uid):
        try:
            self.addEditB.setText('Редагувати')
            self.idTB.setText(str(uid))
            self.hide_author()
            self.hide_aff()
            self.show_pub()

            pub = publications().where(Publication.publication_id == uid).get()
            self.pSubs = subjects().join(PublicationSubject).where(PublicationSubject.publication == uid)
            self.pAffs = affiliations().join(AffiliationPublication).where(AffiliationPublication.publication == uid)
            self.pAuths = authors().join(AuthorPublication).where(AuthorPublication.publication == uid)

            self.pTitleTBL.setText(pub.title)
            self.pDateTBL.setText(str(pub.pub_date))
            self.pCitTBL.setText(f'{pub.cited_by_count} цитувань')
            if pub.url is not None and pub.url != '':
                self.pLinkTBL.setText(f'<a href="{pub.url}">Відкрити публікацію.../</a>')
                self.pLinkTBL.setToolTip(pub.url)
                self.pLinkTBL.linkActivated.connect(self.open_link)
            if pub.abstract == '':
                self.pAbstractL.hide()
            self.pAbstractLRTB.setText(pub.abstract)

            self.fill_pub_authors(self.pAuths)

            self.infoCB.setCurrentIndex(1)

            if self.role == 'Admin':
                self.deleteB.show()
        except Exception as err:
            print(err)

    def fill_pub_authors(self, auth_list):
        self.pubCB.setCurrentIndex(0)
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
        self.setModel(self.pubGrid, df)

    def fill_pub_affiliations(self, aff_list):
        self.pubCB.setCurrentIndex(1)
        items_list = []
        for row in aff_list:
            auths_count = get_authors_count_by_aff_id(row.affiliation_id)
            pubs_count = get_pubs_count_by_aff_id(row.affiliation_id)
            items_list.append(
                [row.affiliation_id, row.affiliation_name, row.city, row.country, row.url, auths_count,
                 pubs_count])
        df = pd.DataFrame(items_list,
                          columns=['id', 'Назва', 'Місто', 'Країна', 'Посилання', 'К-сть авторів',
                                   'К-сть публікацій'])
        self.setModel(self.pubGrid, df)

    def fill_pub_subjects(self, subs_list):
        self.pubCB.setCurrentIndex(2)
        items_list = []
        for row in subs_list:
            items_list.append([row.subject_id, row.full_title, row.group, row.abbreviation, row.code])
        df = pd.DataFrame(items_list,
                          columns=['id', 'Повна назва', 'Група', 'Абревіатура', 'Код'])
        self.setModel(self.pubGrid, df)

    def hide_pub(self):
        self.pTitleTBL.hide()
        self.pDateTBL.hide()
        self.pCitTBL.hide()
        self.pLinkTBL.hide()
        self.pAbstractL.hide()
        self.pAbstractLRTB.hide()

        self.pubCB.hide()
        self.pubGrid.hide()

    def show_pub(self):
        self.pTitleTBL.show()
        self.pDateTBL.show()
        self.pCitTBL.show()
        self.pLinkTBL.show()
        self.pAbstractL.show()
        self.pAbstractLRTB.show()

        self.pubCB.show()
        self.pubGrid.show()

    def delete_pub(self, uid):
        try:
            print(uid)
            with db.atomic():
                pub = publications().where(Publication.publication_id == uid).get()

                AffiliationPublication.delete().where(AffiliationPublication.publication == pub).execute()
                AuthorPublication.delete().where(AuthorPublication.publication == pub).execute()
                PublicationSubject.delete().where(PublicationSubject.publication == pub).execute()

                pub.delete_instance()
                self.hide_pub()
                self.addEditB.setText('Додати')
                self.deleteB.hide()
        except Exception as err:
            print(err)
    # endregion

    # region AUTHOR
    def hide_author(self):
        self.authorL.hide()
        self.aOverviewL.hide()
        self.aTrendL.hide()
        self.aCountWidget.hide()
        self.aCitWidget.hide()
        self.aDocsTBL.hide()
        self.aDocsL.hide()
        self.aCitsCBL.hide()
        self.aCitsL.hide()
        self.aHirshTBL.hide()
        self.aHirshL.hide()

        self.authorCB.hide()
        self.authorGrid.hide()

    def show_author(self):
        self.authorL.show()
        self.aOverviewL.show()
        self.aTrendL.show()
        self.aCountWidget.show()
        self.aCitWidget.show()
        self.aDocsTBL.show()
        self.aDocsL.show()
        self.aCitsCBL.show()
        self.aCitsL.show()
        self.aHirshTBL.show()
        self.aHirshL.show()

        self.authorCB.show()
        self.authorGrid.show()

    def load_author(self, uid):
        try:
            self.addEditB.setText('Редагувати')
            self.idTB.setText(str(uid))
            self.hide_pub()
            self.hide_aff()

            auth = authors().where(Author.author_id == uid).get()

            self.aSubs = subjects().join(AuthorSubject).where(AuthorSubject.author == uid)
            self.aAffs = affiliations().join(AffiliationAuthor).where(AffiliationAuthor.author == uid)
            self.aPubs = publications().join(AuthorPublication).where(AuthorPublication.author == uid)

            years = [p.pub_date.year for p in self.aPubs.group_by(Publication.pub_date.year)]
            years.sort()
            counts = self.sql_count([(1, p.pub_date.year) for p in self.aPubs])
            cits = self.sql_count([(p.cited_by_count, p.pub_date.year)
                                   for p in self.aPubs.order_by(Publication.pub_date)])

            self.authorL.setText(str(auth.name))
            self.aDocsTBL.setText(str(len(self.aPubs)))
            self.aCitsCBL.setText(str(get_citations_count(uid)))
            self.aHirshTBL.setText(str(auth.h_index))

            if len(years) != 0:
                create_bar_chart(self.aCountFig, self.aCountCanvas, years, counts, 'Рік', 'К-сть публікацій',
                                                 'Тенденція публікування')
                create_graph_chart(self.aCitFig, self.aCitCanvas, years, cits, 'Рік', 'К-сть цитувань',
                                   'Тенденція цитування')

            self.fill_author_affiliations(self.aAffs)

            self.show_author()
            self.infoCB.setCurrentIndex(1)

            if self.role == 'Admin':
                self.deleteB.show()
        except Exception as err:
            print(err)

    def fill_author_subjects(self, subs_list):
        self.authorCB.setCurrentIndex(2)
        items_list = []
        for row in subs_list:
            items_list.append([row.subject_id, row.full_title, row.group, row.abbreviation, row.code])
        df = pd.DataFrame(items_list,
                          columns=['id', 'Повна назва', 'Група', 'Абревіатура', 'Код'])
        self.setModel(self.authorGrid, df)

    def fill_author_publications(self, pubs_list):
        self.authorCB.setCurrentIndex(1)
        items_list = []
        for row in pubs_list:
            auth_list = get_authors_by_pub_id(row.publication_id)
            aff_list = get_affiliations_by_pub_id(row.publication_id)
            sub_list = get_subjects_by_publication_id(row.publication_id)
            sources = get_sources(row)
            items_list.append(
                    [row.publication_id, row.title, row.abstract, row.url, row.cited_by_count, sub_list, row.keywords,
                     row.pub_date, auth_list, aff_list, sources])
        df = pd.DataFrame(items_list,
                              columns=['id', 'Назва', 'Анотація', 'Посилання', 'К-сть цитувань', 'Теми',
                                       'Ключові слова',
                                       'Дата публікації', 'Автори', 'Організації', 'Джерела'])
        self.setModel(self.authorGrid, df)

    def fill_author_affiliations(self, affs_list):
        self.authorCB.setCurrentIndex(0)
        items_list = []
        for row in affs_list:
            auths_count = get_authors_count_by_aff_id(row.affiliation_id)
            pubs_count = get_pubs_count_by_aff_id(row.affiliation_id)
            items_list.append(
                [row.affiliation_id, row.affiliation_name, row.city, row.country, row.url, auths_count,
                 pubs_count])
        df = pd.DataFrame(items_list,
                          columns=['id', 'Назва', 'Місто', 'Країна', 'Посилання', 'К-сть авторів',
                                   'К-сть публікацій'])
        self.setModel(self.authorGrid, df)

    def delete_author(self, uid):
        with db.atomic():
            author = authors().where(Author.author_id == uid).get()

            AuthorPublication.delete().where(AuthorPublication.author == author).execute()
            AffiliationAuthor.delete().where(AffiliationAuthor.author == author).execute()
            AuthorSubject.delete().where(AuthorSubject.author == author).execute()

            author.delete_instance()
            self.hide_author()
            self.addEditB.setText('Додати')
            self.deleteB.hide()
    # endregion
    # region AFFILIATION

    def load_affiliation(self, uid):
        try:
            self.idTB.setText(str(uid))
            self.addEditB.setText('Редагувати')
            self.hide_pub()
            self.hide_author()

            aff = affiliations().where(Affiliation.affiliation_id == uid).get()
            self.oPubs = publications().join(AffiliationPublication).where(AffiliationPublication.affiliation == uid)
            self.oAuthors = authors().join(AffiliationAuthor).where(AffiliationAuthor.affiliation == uid)

            self.oNameTBL.setText(aff.affiliation_name)
            if aff.city is not None:
                loc = aff.city
                if aff.country is not None:
                    loc = f'{loc}, {aff.country}'
                self.oLocationTBL.setText(loc)
            elif aff.country is not None:
                self.oLocationTBL.setText(aff.country)

            if aff.address is not None:
                self.oAddressTBL.setText(aff.address)

            if aff.url is not None:
                self.oLinkTBL.setText(f'<a href="{aff.url}">Відкрити організацію.../</a>')
                self.oLinkTBL.setToolTip(aff.url)
                self.oLinkTBL.linkActivated.connect(self.open_link)

            topics = self.get_topics(self.oPubs)
            create_pie_chart(self.oTopFig, self.oTopCanvas, topics.values(), topics.keys())
            self.fill_aff_publications(self.oPubs)
            self.show_aff()
            self.infoCB.setCurrentIndex(2)

            if self.role == 'Admin':
                self.deleteB.show()
        except Exception as err:
            print(err)

    def get_topics(self, pubs):
        subs = []
        for row in pubs:
            if row.scopus_id is not None:
                s = get_abbs_by_publication_id(row.publication_id)
                subs.extend(s.split(', '))

        dick = dict()
        for s in subs:
            if s in dick:
                dick[s] += 1
            else:
                dick[s] = 1

        return dict(Counter(dick).most_common(10))

    def hide_aff(self):
        self.oNameTBL.hide()
        self.oLocationTBL.hide()
        self.oAddressTBL.hide()
        self.oLinkTBL.hide()

        self.oTopicL.hide()
        self.oTopWidget.hide()

        self.affCB.hide()
        self.affGrid.hide()

    def show_aff(self):
        self.oNameTBL.show()
        self.oLocationTBL.show()
        self.oAddressTBL.show()
        self.oLinkTBL.show()

        self.oTopicL.show()
        self.oTopWidget.show()

        self.affCB.show()
        self.affGrid.show()

    def fill_aff_authors(self, auth_list):
        self.affCB.setCurrentIndex(0)
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
        self.setModel(self.affGrid, df)

    def fill_aff_publications(self, pubs_list):
        self.affCB.setCurrentIndex(1)
        try:
            items_list = []
            for row in pubs_list:
                auth_list = get_authors_by_pub_id(row.publication_id)
                aff_list = get_affiliations_by_pub_id(row.publication_id)
                sub_list = get_subjects_by_publication_id(row.publication_id)
                sources = get_sources(row)
                items_list.append(
                    [row.publication_id, row.title, row.abstract, row.url, row.cited_by_count, sub_list, row.keywords,
                     row.pub_date, auth_list, aff_list, sources])
            df = pd.DataFrame(items_list,
                                  columns=['id', 'Назва', 'Анотація', 'Посилання', 'К-сть цитувань', 'Теми',
                                           'Ключові слова',
                                           'Дата публікації', 'Автори', 'Організації', 'Джерела'])
            self.setModel(self.affGrid, df)
        except Exception as err:
            print(err)

    def delete_aff(self, uid):
        with db.atomic():
            aff = affiliations().where(Affiliation.affiliation_id == uid).get()

            AffiliationAuthor.delete().where(AffiliationAuthor.affiliation == aff).execute()
            AffiliationPublication.delete().where(AffiliationPublication.affiliation == aff).execute()

            aff.delete_instance()
            self.hide_aff()
            self.addEditB.setText('Додати')
            self.deleteB.hide()
    # endregion
    # endregion

