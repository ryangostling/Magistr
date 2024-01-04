# External
from PyQt5.QtCore import QObject


class Updater(QObject):
    def __init__(self, update):
        super().__init__()
        self.update = update

    def run(self):
        try:
            self.update()
        except Exception as err:
            print(err)
