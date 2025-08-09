from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets.Components import *

from assets import *

##############################################################################################################################

class Table_APIKeys(TableBase):
    """
    """
    valueChanged = Signal(dict)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setRowCount(0)
        self.setColumnCount(0)
        self.setIndexHeaderVisible(False)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.model().dataChanged.connect(
            lambda: self.valueChanged.emit(self.getValue())
        )

    def setStyleSheet(self, styleSheet: str):
        super().setStyleSheet(styleSheet + '''
            QHeaderView::section, QTableView::item {padding: 0px;}
        '''
        )

    def addRow(self, param: tuple):
        sourceName, apiKey = param

        rowHeight = 30
        def _setColumnLayout(columnLayout):
            columnLayout.setContentsMargins(0, 0, 0, 0)
            columnLayout.setSpacing(0)

        label_sourceName = LabelBase()
        label_sourceName.setAlignment(Qt.AlignCenter)
        QFunc.setText(label_sourceName, sourceName)
        column0Layout = QHBoxLayout()
        _setColumnLayout(column0Layout)
        column0Layout.addWidget(label_sourceName)

        lineEdit = LineEditBase()
        lineEdit.setBorderless(True)
        lineEdit.setTransparent(True)
        lineEdit.textChanged.connect(
            lambda: self.valueChanged.emit(self.getValue())
        )
        QFunc.setText(lineEdit, apiKey)
        column1Layout = QHBoxLayout()
        _setColumnLayout(column1Layout)
        column1Layout.addWidget(lineEdit)

        super().addRow(
            [column0Layout, column1Layout],
            [QHeaderView.Fixed, QHeaderView.Stretch],
            [None, None],
            rowHeight
        )

    def setValue(self, params: dict = {'%Source%': '%APIKey%'}):
        self.clearRows()
        super().setColumnCount(self.columnCount())
        for key, value in (params if isinstance(params, dict) else eval(params)).items():
            QApplication.instance().processEvents()
            param = (key, value)
            self.addRow(param)

    def getValue(self):
        valueDict = {}
        for rowCount in range(self.rowCount()):
            try:
                key = QFunc.getText(self.cellWidget(rowCount, 0).findChild(QLabel))
                value = QFunc.getText(self.cellWidget(rowCount, 1).findChild(QLineEdit))
                valueDict[key] = value
            except:
                pass
        return valueDict

##############################################################################################################################