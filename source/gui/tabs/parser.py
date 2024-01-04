# External
from multiprocessing import Lock
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar

# Internal
from gui.misc.signalsWrapper import SignalsWrapper
from gui.misc.updater import Updater
from parsers.parser import Parser

redrawLock = Lock()
updateLock = Lock()

class ParserTab:
    # region SETUP

    def __init__(self, page, update):
        self.page = page
        self.update = update
        self.setup_ui()
        self.setup_events()
        self.searchers = []
        self.relations = {'І': ' and ', 'АБО': ' or '}
        self.criterias = {'Автор': 'AUTH({})', 'Організація': 'AFFIL({})', 'Назва': 'TITLE(\"{}\")'}
        self.shift = 40
        self.pos = 50
        self.parser = None
        self.parseThread = None
        self.updateThread = None
        self.updater = None

    def setup_ui(self):
        self.intValidator = QIntValidator()

        self.addSearcherB = QPushButton(self.page)
        self.addSearcherB.setText('Додати критерій пошуку')
        self.progressBar = QProgressBar(self.page)
        self.progressBar.setProperty("value", 0)
        self.progressL = QLabel(self.page)
        self.progressL.setText('')
        self.progressL.setAlignment(Qt.AlignHCenter)
        self.progressL.setWordWrap(True)
        self.searchFromL = QLabel(self.page)
        self.searchFromL.setText('З')
        self.searchFromTB = QLineEdit(self.page)
        self.searchFromTB.setValidator(self.intValidator)
        self.searchToL = QLabel(self.page)
        self.searchToL.setText('До')
        self.searchToTB = QLineEdit(self.page)
        self.searchToTB.setValidator(self.intValidator)
        self.searchB = QPushButton(self.page)
        self.searchB.setText('Пошук')
        self.searchB.setEnabled(False)

        self.addSearcherB.setGeometry(10, 10, 200, 30)
        self.searchFromL.setGeometry(10, 50, 10, 30)
        self.searchFromTB.setGeometry(30, 50, 100, 30)
        self.searchToL.setGeometry(140, 50, 20, 30)
        self.searchToTB.setGeometry(170, 50, 100, 30)
        self.progressBar.setGeometry(1450, 50, 320, 30)
        self.searchB.setGeometry(1780, 50, 100, 30)
        self.progressL.setGeometry(1450, 90, 300, 60)

    def setup_events(self):
        self.searchB.clicked.connect(self.on_searchB_clicked)
        self.addSearcherB.clicked.connect(self.on_addSearcherB_clicked)
    # endregion
    # region EVENTS

    def on_addSearcherB_clicked(self):
        searcher = []
        if len(self.searchers) != 0:
            relationCB = QComboBox(self.page)
            relationCB.addItems(self.relations.keys())
            relationCB.setCurrentIndex(0)
            relationCB.setGeometry(10, self.pos, 50, 30)
            self.pos += self.shift
            searcher.append(relationCB)
        else:
            self.searchB.setEnabled(True)
        criteriaL = QLabel(self.page)
        criteriaL.setText('Критерій')
        criteriaL.setGeometry(10, self.pos, 50, 30)
        searcher.insert(0, criteriaL)

        criteriaCB = QComboBox(self.page)
        criteriaCB.addItems(self.criterias.keys())
        criteriaCB.setCurrentIndex(0)
        criteriaCB.setGeometry(70, self.pos, 100, 30)
        searcher.insert(1, criteriaCB)

        searchTB = QLineEdit(self.page)
        searchTB.setGeometry(180, self.pos, 1590, 30)
        searcher.insert(2, searchTB)

        removeB = QPushButton(self.page)
        removeB.setText('Видалити')
        removeB.setGeometry(1780, self.pos, 100, 30)
        searcher.insert(3, removeB)
        removeB.clicked.connect(self.on_removeB_clicked)

        self.pos += self.shift
        for i in searcher:
            i.show()
        self.searchers.append(searcher)
        self.searchFromL.move(self.searchFromL.x(), self.pos)
        self.searchFromTB.move(self.searchFromTB.x(), self.pos)
        self.searchToL.move(self.searchToL.x(), self.pos)
        self.searchToTB.move(self.searchToTB.x(), self.pos)
        self.progressBar.move(self.progressBar.x(), self.pos)
        self.progressL.move(self.progressL.x(), self.pos + self.shift)
        self.searchB.move(self.searchB.x(), self.pos)

    def on_removeB_clicked(self):
        sender = self.page.sender()
        if len(self.searchers) > 1:
            shift = 2 * self.shift
        else:
            shift = self.shift

        for i in range(len(self.searchers)):
            if sender in self.searchers[i]:
                idx = i
                break

        for i in self.searchers[idx:]:
            for j in i:
                j.move(j.x(), j.y() - shift)

        for i in self.searchers[idx]:
            i.close()
            i.deleteLater()

        self.pos -= shift
        self.searchFromL.move(self.searchFromL.x(), self.pos)
        self.searchFromTB.move(self.searchFromTB.x(), self.pos)
        self.searchToL.move(self.searchToL.x(), self.pos)
        self.searchToTB.move(self.searchToTB.x(), self.pos)
        self.progressBar.move(self.progressBar.x(), self.pos)
        self.searchB.move(self.searchB.x(), self.pos)
        self.progressL.move(self.progressL.x(), self.pos + self.shift)
        self.searchers.pop(idx)

        if len(self.searchers) == 0:
            self.searchB.setEnabled(False)

    def on_searchB_clicked(self):
        try:
            text = self.searchB.text()

            if text == 'Пошук':
                self.search()
            else:
                self.abort()
        except Exception as err:
            print(err)
    # endregion
    # region HANDLERS

    def progress_bar_handler(self, value):
        with redrawLock:
            self.progressBar.setValue(value)

    def progress_bar_max_handler(self, maximum):
        try:
            with redrawLock:
                self.progressBar.setMaximum(maximum)
        except Exception as err:
            print(f'error: {err}')

    def progress_label_handler(self, status):
        self.progressL.setText(status)

    def results_handler(self):
        try:
            self.progressBar.setValue(0)
            self.progressL.setText('')
            self.searchB.setText('Пошук')
            for i in self.searchers:
                i[3].setEnabled(True)
        except Exception as err:
            print(err)

    def update_handler(self):
        try:
            with updateLock:
                if self.updateThread is not None:
                    self.updateThread.terminate()

                self.updateThread = QThread()
                self.updater = Updater(self.update)
                self.updater.moveToThread(self.updateThread)
                self.updateThread.started.connect(self.updater.run)
                self.updateThread.start()
        except Exception as err:
            print(err)

    def search(self):
        try:
            query = ''
            if len(self.searchers) == 0:
                return
            text = self.searchers[0][2].text()
            criteria = self.criterias[self.searchers[0][1].currentText()]
            if text == '':
                return
            else:
                query += criteria.format(text)

            for i in range(1, len(self.searchers)):
                text = self.searchers[i][2].text()
                criteria = self.criterias[self.searchers[i][1].currentText()]
                relation = self.relations[self.searchers[i][4].currentText()]
                if text == '':
                    return
                query += relation + criteria.format(text)

            dateFrom = self.searchFromTB.text()
            dateTo = self.searchToTB.text()

            if dateFrom != '' or dateTo != '':
                query = f'({query})'
                if dateFrom != '':
                    query += f' and PUBYEAR AFT {dateFrom}'
                if dateTo != '':
                    query += f' and PUBYEAR BEF {dateTo}'

            self.searchB.setText('Зупинити')
            for i in self.searchers:
                i[3].setEnabled(False)

            wrapper = SignalsWrapper()
            wrapper.progress_signal.connect(self.progress_bar_handler)
            wrapper.set_max_signal.connect(self.progress_bar_max_handler)
            wrapper.status_signal.connect(self.progress_label_handler)
            wrapper.results_signal.connect(self.results_handler)
            wrapper.update_signal.connect(self.update_handler)

            if self.parseThread is not None:
                self.parseThread.terminate()

            self.parseThread = QThread()
            self.parser = Parser(query, wrapper)
            self.parser.moveToThread(self.parseThread)
            self.parseThread.started.connect(self.parser.run)
            self.parseThread.start()

        except Exception as err:
            print(err)

    def abort(self):
        try:
            self.parser.abort()
        except Exception as err:
            print(err)

    # endregion
