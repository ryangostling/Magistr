# External
from PyQt5.QtCore import QObject, pyqtSignal


class SignalsWrapper(QObject):
    progress_signal = pyqtSignal(int)
    set_max_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    results_signal = pyqtSignal()
    update_signal = pyqtSignal()
