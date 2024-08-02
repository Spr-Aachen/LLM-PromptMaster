import pandas
from PySide6.QtWidgets import *
from QEasyWidgets.Utils import *
from QEasyWidgets.QTasks import *
from QEasyWidgets.WindowCustomizer import *

from windows.ui.UI_Window import *

##############################################################################################################################

class Window_MainWindow(ChildWindowBase):
    ui = Ui_Window()

    def __init__(self, parent = None):
        super().__init__(parent, min_width = 1280, min_height = 720)

        self.ui.setupUi(self)

        self.setTitleBar(self.ui.TitleBar)

##############################################################################################################################

class TestWindow(DialogBase):
    '''
    Dialog Window
    '''
    QuestionList = []

    def __init__(self, parent = None):
        super().__init__(parent)

        self.resize(360, 240)

    def initUI(self):
        self.Label = QLabel()
        self.Label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.LineEdit_FilePath = LineEditBase()

        self.LineEdit_Column = LineEditBase()

        self.LineEdit_Amount = LineEditBase()

        self.Button_Confirm = QPushButton('Confirm', self)

        self.Button_Cancel = QPushButton('Cancel', self)

        Layout = QGridLayout(self)
        Layout.addWidget(self.Label, 0, 0, 1, 2)
        Layout.addWidget(self.LineEdit_FilePath, 1, 0, 1, 2)
        Layout.addWidget(self.LineEdit_Column, 2, 0, 1, 2)
        Layout.addWidget(self.LineEdit_Amount, 3, 0, 1, 2)
        Layout.addWidget(self.Button_Confirm, 4, 0, 1, 1)
        Layout.addWidget(self.Button_Cancel, 4, 1, 1, 1)
        Layout.setRowStretch(0, 1)

    def LoadQuestions(self):
        FilePath = self.LineEdit_FilePath.text()
        if Path(FilePath).exists():
            excelDF = pandas.read_excel(FilePath, usecols = self.LineEdit_Column.text().strip())
            self.QuestionList = excelDF.iloc[:, 0].to_list()
        MaximumAmount = self.LineEdit_Amount.text().strip()
        if MaximumAmount.__len__() > 0 and self.QuestionList.__len__() > int(MaximumAmount) > 0 :
            self.QuestionList = self.QuestionList[:int(MaximumAmount)]

    def exec(self):
        self.initUI()

        self.Label.setText("Plz provide ur excel file path and its column letter:")

        self.LineEdit_FilePath.SetFileDialog('SelectFile', '表格 (*.csv *.xlsx)')
        self.LineEdit_FilePath.setAcceptDrops(True)
        self.LineEdit_FilePath.setPlaceholderText("Please enter the excel file path to load")

        self.LineEdit_Column.RemoveFileDialogButton()
        self.LineEdit_Column.setAcceptDrops(False)
        self.LineEdit_Column.setPlaceholderText("Please enter the column where questions are located")

        self.LineEdit_Amount.RemoveFileDialogButton()
        self.LineEdit_Amount.setAcceptDrops(False)
        self.LineEdit_Amount.setPlaceholderText("Please enter the maximum amount of questions")

        self.Button_Confirm.clicked.connect(self.LoadQuestions, Qt.ConnectionType.QueuedConnection)
        self.Button_Confirm.clicked.connect(self.close, Qt.ConnectionType.QueuedConnection)

        self.Button_Cancel.clicked.connect(self.close)

        super().exec()

##############################################################################################################################