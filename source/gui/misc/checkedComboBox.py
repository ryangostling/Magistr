# External
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QComboBox


# new check-able combo box
class CheckedComboBox(QComboBox):
    # constructor
    def __init__(self, parent=None):
        super(CheckedComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))

    counter = 0

    def clearSelection(self):
        try:
            for item in self.items():
                item.setCheckState(Qt.Unchecked)
            self.setCurrentText('')
            self.setCurrentIndex(-1)
        except Exception as err:
            print(err)

    def selectAll(self):
        try:
            for item in self.items():
                item.setCheckState(Qt.Checked)
            self.setCurrentText('')
            self.setCurrentIndex(-1)
        except Exception as err:
            print(err)

    def items(self):
        return [self.model().itemFromIndex(self.model().index(i, 0)) for i in range(self.count())]

    def hasSelection(self):
        return any([item.checkState() == Qt.Checked for item in self.items()])

    def getChecked(self):
        return list(filter(lambda item: item.checkState() == Qt.Checked, self.items()))

    def getCheckedTexts(self):
        return [i.text() for i in self.getChecked()]

    def getUnchecked(self):
        return list(filter(lambda item: item.checkState() == Qt.Unchecked, self.items()))

    def getCheckedIndices(self):
        checked = self.getChecked()
        items = self.items()
        indices = []
        for i in range(len(items)):
            if items[i] in checked:
                indices.append(i)
        return indices

    def selectAll(self):
        for i in range(len(self.items())):
            self.handleItemPressed(self.model().index(i, 0))

    def selectLast(self):
        l = len(self.items())
        if l != 0:
            self.handleItemPressed(self.model().index(l - 1, 0))

    # when any item get pressed
    def handleItemPressed(self, index):
        # getting the item
        item = self.model().itemFromIndex(index)
        # checking if item is checked
        if item.checkState() == Qt.Checked:
            # making it unchecked
            item.setCheckState(Qt.Unchecked)
        # if not checked
        else:
            # making the item checked
            item.setCheckState(Qt.Checked)
            self.counter += 1
