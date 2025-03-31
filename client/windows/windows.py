import os
import pandas
from pathlib import Path
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QStandardItem, QFont
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets.Components import ListBase
from QEasyWidgets.Windows import MainWindowBase, DialogBase, MessageBoxBase, InputDialogBase

from ui import *

##############################################################################################################################

class Window_MainWindow(MainWindowBase):
    ui = Ui_MainWindow()

    def __init__(self, parent = None):
        super().__init__(parent, min_width = 900, min_height = 600)

        self.ui.setupUi(self)

        self.setTitleBar(self.ui.titleBar)

        self.setCentralWidget(self.ui.centralWidget)

        self.langChanged.connect(lambda: self.ui.retranslateUi(self))

##############################################################################################################################

class Window_PromptWindow(DialogBase):
    """
    Dialog to manage prompt
    """
    def __init__(self, parent = None):
        super().__init__(parent)

        self.titleArea = LabelBase()
        self.titleArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titleArea.setFont(QFont('Arial', 21))

        layout_title = QHBoxLayout()
        layout_title.addWidget(self.titleArea)
        layout_title.setContentsMargins(0, 0, 0, 0)
        layout_title.setSpacing(12)

        self.button_createPrompt = HollowButton()
        self.button_deletePrompt = HollowButton()
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_createPrompt)
        layout_buttons.addWidget(self.button_deletePrompt)

        self.listWidget = ListBase()

        layout_left = QVBoxLayout()
        layout_left.addLayout(layout_buttons)
        layout_left.addWidget(self.listWidget)
        layout_left.setStretch(1, 1)
        layout_left.setContentsMargins(0, 0, 0, 0)
        layout_left.setSpacing(12)

        self.textEdit = TextEditBase()

        layout_right = QGridLayout()
        layout_right.addWidget(self.textEdit)
        layout_right.setContentsMargins(0, 0, 0, 0)

        layout = QGridLayout(self)
        layout.addLayout(layout_title, 0, 0)
        layout.addLayout(layout_left, 1, 0)
        layout.addLayout(layout_right, 1, 1)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)


class Window_LoadWindow(DialogBase):
    '''
    Dialog to load questions from file
    '''
    questionList = []

    def __init__(self, parent = None):
        super().__init__(parent)

        self.resize(360, 240)

        self.titleBar.closeButton.hide()
        self.titleBar.closeButton.deleteLater()

        self.label = LabelBase()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lineEdit_filePath = LineEditBase()

        self.lineEdit_column = LineEditBase()

        self.lineEdit_amount = LineEditBase()

        self.button_confirm = QPushButton('Confirm', self)

        self.button_cancel = QPushButton('Cancel', self)

        layout = QGridLayout(self)
        layout.addWidget(self.label, 0, 0, 1, 2)
        layout.addWidget(self.lineEdit_filePath, 1, 0, 1, 2)
        layout.addWidget(self.lineEdit_column, 2, 0, 1, 2)
        layout.addWidget(self.lineEdit_amount, 3, 0, 1, 2)
        layout.addWidget(self.button_confirm, 4, 0, 1, 1)
        layout.addWidget(self.button_cancel, 4, 1, 1, 1)
        layout.setRowStretch(0, 1)

##############################################################################################################################