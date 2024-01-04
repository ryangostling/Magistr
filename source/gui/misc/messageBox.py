# External
from PyQt5.QtWidgets import QMessageBox


def show_message(text):
    msg = QMessageBox()
    msg.setText(text)
    msg.setStyleSheet('QLabel{min-width: 250px;}')
    msg.exec()
