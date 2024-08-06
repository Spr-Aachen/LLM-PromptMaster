import pandas
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets.Windows import *

from windows.ui.UI_Window import *

##############################################################################################################################

class Window_MainWindow(ChildWindowBase):
    ui = Ui_Window()

    def __init__(self, parent = None):
        super().__init__(parent, min_width = 1280, min_height = 720)

        self.ui.setupUi(self)

        self.setTitleBar(self.ui.TitleBar)

##############################################################################################################################

class PromptWindow(DialogBase):
    '''
    Dialog to manage prompt
    '''
    PromptDict = {}

    def __init__(self, parent = None, PromptDir = ...):
        super().__init__(parent)

        self.PromptDir = PromptDir

    def initUI(self):
        self.TitleArea = QLabel()
        self.TitleArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.TitleArea.setStyleSheet('font-size: 21px;')

        Layout_Title = QHBoxLayout()
        Layout_Title.addWidget(self.TitleArea)
        Layout_Title.setContentsMargins(0, 0, 0, 0)
        Layout_Title.setSpacing(12)

        self.Button_CreatePrompt = QPushButton()
        self.Button_DeletePrompt = QPushButton()
        Layout_Buttons = QHBoxLayout()
        Layout_Buttons.addWidget(self.Button_CreatePrompt)
        Layout_Buttons.addWidget(self.Button_DeletePrompt)

        self.ListWidget = QListWidget()

        Layout_Left = QVBoxLayout()
        Layout_Left.addLayout(Layout_Buttons)
        Layout_Left.addWidget(self.ListWidget)
        Layout_Left.setStretch(1, 1)
        Layout_Left.setContentsMargins(0, 0, 0, 0)
        Layout_Left.setSpacing(12)

        self.TextEdit = TextEditBase()

        Layout_Right = QGridLayout()
        Layout_Right.addWidget(self.TextEdit)
        Layout_Right.setContentsMargins(0, 0, 0, 0)

        Layout = QGridLayout(self)
        Layout.addLayout(Layout_Title, 0, 0)
        Layout.addLayout(Layout_Left, 1, 0)
        Layout.addLayout(Layout_Right, 1, 1)
        Layout.setContentsMargins(12, 12, 12, 12)
        Layout.setSpacing(12)

    def loadCurrentPrompt(self, item: QListWidgetItem):
        # Load a conversation from a txt file and display it in the browser
        self.PromptFilePath = Path(self.PromptDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.PromptFilePath, 'r', encoding = 'utf-8') as f:
            Prompt = f.read()
        self.TextEdit.setText(Prompt)

    def removePromptFile(self, listItem: QListWidgetItem):
        self.ListWidget.takeItem(self.ListWidget.row(listItem))
        os.remove(Path(self.PromptDir).joinpath(listItem.text() + '.txt').as_posix())

    def renamePrompt(self):
        currentItem = self.ListWidget.currentItem()
        if currentItem is not None:
            old_name = currentItem.text()
            new_name, ok = QInputDialog.getText(self,
                'Rename Prompt',
                'Enter new prompt name:'
            )
            if ok and new_name:
                self.PromptFilePath = Path(self.PromptDir).joinpath(f"{new_name}.txt").as_posix()
                os.rename(Path(self.PromptDir).joinpath(f"{old_name}.txt"), self.PromptFilePath)
                currentItem.setText(new_name)
                # Transfer&Remove message
                self.PromptDict[new_name] = self.PromptDict[old_name]
                self.PromptDict.pop(old_name)

    def deletePrompt(self):
        currentItem = self.ListWidget.currentItem()
        if currentItem is not None:
            old_name = currentItem.text()
            confirm = QMessageBox.question(self,
                'Delete Prompt',
                'Are you sure you want to delete this Prompt?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.removePromptFile(currentItem)
                self.TextEdit.clear()
                if self.ListWidget.count() > 0:
                    self.loadCurrentPrompt(self.ListWidget.currentItem())
                # Remove message
                self.PromptDict.pop(old_name)

    def createPrompt(self):
        PromptName, ok = QInputDialog.getText(self,
            'Rename Prompt',
            'Enter new prompt name:'
        )
        if ok and PromptName:
            self.PromptFilePath = Path(self.PromptDir).joinpath(f"{PromptName}.txt").as_posix()
            # Check if the path would be overwritten & Update the history file path
            self.PromptFilePath = QFunc.RenameFile(self.PromptFilePath)
            PromptName = Path(self.PromptFilePath).stem
            # Set the files & browser
            with open(self.PromptFilePath, 'w', encoding = 'utf-8') as f:
                f.write('')
            self.TextEdit.clear()
            # Add the given name to the history list and select it
            NewPrompt = QListWidgetItem(PromptName)
            self.ListWidget.addItem(NewPrompt)
            self.ListWidget.setCurrentItem(NewPrompt)
            # Init message
            self.PromptDict[PromptName] = []

    def ShowContextMenu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Delete Prompt", self)
        delete_action.triggered.connect(self.deletePrompt)
        rename_action = QAction("Rename Prompt", self)
        rename_action.triggered.connect(self.renamePrompt)
        context_menu.addActions([delete_action, rename_action])
        context_menu.exec(self.ListWidget.mapToGlobal(position))

    def LoadPromptList(self):
        # Check if the prompt directory exists
        if not os.path.exists(self.PromptDir):
            os.makedirs(self.PromptDir)
        # Remove empty prompt and add the rest to history list
        self.ListWidget.clear()
        for HistoryFileName in os.listdir(self.PromptDir):
            if HistoryFileName.endswith('.txt'):
                HistoryFilePath = Path(self.PromptDir).joinpath(HistoryFileName).as_posix()
                if os.path.getsize(HistoryFilePath) == 0:
                    os.remove(HistoryFilePath)
                    continue
                self.ListWidget.addItem(HistoryFileName[:-4]) # Remove the .txt extension

    def savePrompt(self, Prompt: str):
        if self.ListWidget.count() == 0:
            return
        with open(self.PromptFilePath, 'w', encoding = 'utf-8') as f:
            PromptStr = Prompt.strip()
            f.write(PromptStr)

    def exec(self):
        self.initUI()

        self.TitleArea.setText('Prompt Manager')

        self.TextEdit.textChanged.connect(self.savePrompt)
        self.TextEdit.setPlaceholderText(
            """
            请在此区域输入Prompt
            """
        )

        self.Button_CreatePrompt.setText('Create Prompt')
        self.Button_CreatePrompt.clicked.connect(self.createPrompt)

        self.Button_DeletePrompt.setText('Delete Prompt')
        self.Button_DeletePrompt.clicked.connect(self.deletePrompt)

        self.ListWidget.itemClicked.connect(self.loadCurrentPrompt)
        self.ListWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ListWidget.customContextMenuRequested.connect(self.ShowContextMenu)

        # Load prompt
        self.LoadPromptList()

        super().exec()


class TestWindow(DialogBase):
    '''
    Dialog to load questions from file
    '''
    QuestionList = []

    def __init__(self, parent = None):
        super().__init__(parent)

        self.resize(360, 240)

        self.TitleBar.CloseButton.hide()
        self.TitleBar.CloseButton.deleteLater()

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