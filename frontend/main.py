# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
import pytz
from datetime import date, datetime
from typing import Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtGui import QTextCursor, QAction
from PySide6.QtWidgets import *
from QEasyWidgets.Utils import *
from QEasyWidgets.QTasks import *
from QEasyWidgets.WindowCustomizer import *

from Functions import *
from windows.Windows import *
from config import *

##############################################################################################################################

def BuildMessageMarkdown(messages: list[dict]):
    markdown = ""
    for message in messages:
        role = str(message['role']).strip()
        content = str(message['content']).strip()
        if len(content) == 0:
            continue
        if role == 'user':
            markdown += f"**Q**: {content}\n\n\n"
        if role == 'assistant':
            markdown += f"**A**: {content}\n\n"
            markdown += "---------------------------------------\n\n"
    return markdown


def chatRequest(
    #env: str = 'uat',
    protocol: str = 'http',
    ip: str = 'localhost',
    port: Optional[int] = None,
    type: str = 'assistant',
    model: Optional[str] = None,
    messages: list[dict] = [{}],
    options: Optional[dict] = None,
    testtimes: Optional[int] = None
):
    # 双Token身份验证，获取令牌
    if port is None:
        port = 80 if protocol == 'http' else 443
    Headers = {
        'P-Rtoken': "...",
        'P-Auth': "...",
        "P-AppId": "..."
    }
    response = requests.get(
        url = f"{protocol}://{ip}:{port}/auth",
        headers = Headers
    )
    if response.status_code == 200:
        res_token = response.json()
        Token = res_token.get("data", {})
        oauth_token = f"Bearer {Token}"
    else:
        return "Request failed", response.status_code

    # gpt/智能体接口请求
    if type == 'gpt':
        type = f"{type}?model={'gpt-4o' if model is None else model}"
    if testtimes is not None:
        assert testtimes > 1, "testtimes must be greater than 1"
        URL = f"{protocol}://{ip}:{port}/{type}?testtimes={testtimes}"
    else:
        URL = f"{protocol}://{ip}:{port}/{type}"
    Headers = {
        'Authorization': oauth_token
    }
    Payload = {
        'message': messages,
        'options': options
    } if options is not None else {
        'message': messages
    }
    response = requests.post(
        url = URL,
        headers = Headers,
        data = json.dumps(Payload)
    )
    if response.status_code == 200:
        content = ""
        for chunk in response.iter_content(chunk_size = 1024, decode_unicode = True):
            if chunk:
                content += chunk#.decode('utf-8')
                try:
                    parsed_content = json.loads(content)
                    return parsed_content['data'], response.status_code
                except json.JSONDecodeError:
                    continue
    else:
        return "Request failed", response.status_code


def exitRequest(
    protocol: str = 'http',
    ip: str = 'localhost',
    port: Optional[int] = None
):
    response = requests.post(
        url = f"{protocol}://{ip}:{port}/actuator/shutdown"
    )
    return json.loads(response.text) if response.status_code == 200 else "服务未能关闭", response.status_code

##############################################################################################################################

class RequestThread(QThread):
    textReceived = Signal(str)

    def __init__(self,
        #env: str = 'uat',
        protocol: str = 'http',
        ip: str = 'localhost',
        port: Optional[int] = None,
        type: str = 'assistant',
        model: Optional[str] = None,
        messages: list[dict] = [{}],
        options: Optional[dict] = None,
        testtimes: Optional[int] = None
    ):
        super().__init__()

        #self.env = env
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.type = type
        self.model = model
        self.messages = messages
        self.options = options
        self.testtimes = testtimes

    def run(self):
        result, statuscode = chatRequest(
            #env = self.env,
            protocol = self.protocol,
            ip = self.ip,
            port = self.port,
            type = self.type,
            model = self.model,
            messages = self.messages,
            options = self.options,
            testtimes = self.testtimes
        )
        self.textReceived.emit(result if statuscode == 200 else "请求失败")

##############################################################################################################################

class MainWindow(Window_MainWindow):
    '''
    Main Window
    '''
    roles = {"无": ""}

    MessagesDict = {}

    thread = None

    def __init__(self):
        super().__init__()

        self.resize(900, 600)

    def applyRole(self):
        '''
        for ConversationName, Messages in self.MessagesDict.items():
            Messages.append(
                {
                    'role': 'assistant',
                    'content': self.roles[self.ComboBox_Role.currentText()]
                }
            )
            self.MessagesDict[ConversationName] = Messages
        '''

    def removeConversationFiles(self, listItem: QListWidgetItem):
        self.ui.ListWidget_Conversation.takeItem(self.ui.ListWidget_Conversation.row(listItem))
        os.remove(Path(ConversationDir).joinpath(listItem.text() + '.txt').as_posix())
        os.remove(Path(QuestionDir).joinpath(listItem.text() + '.txt').as_posix())

    def renameConversation(self):
        currentItem = self.ui.ListWidget_Conversation.currentItem()
        if currentItem is not None:
            old_name = currentItem.text()
            new_name, ok = QInputDialog.getText(self,
                'Rename Conversation',
                'Enter new conversation name:'
            )
            if ok and new_name:
                self.ConversationFilePath = Path(ConversationDir).joinpath(f"{new_name}.txt").as_posix()
                os.rename(Path(ConversationDir).joinpath(f"{old_name}.txt"), self.ConversationFilePath)
                currentItem.setText(new_name)
                self.QuestionFilePath = Path(QuestionDir).joinpath(f"{new_name}.txt").as_posix()
                os.rename(Path(QuestionDir).joinpath(f"{old_name}.txt"), self.QuestionFilePath)
                # Transfer&Remove message
                self.MessagesDict[new_name] = self.MessagesDict[old_name]
                self.MessagesDict.pop(old_name)
                self.applyRole()

    def deleteConversation(self):
        currentItem = self.ui.ListWidget_Conversation.currentItem()
        if currentItem is not None:
            old_name = currentItem.text()
            confirm = QMessageBox.question(self,
                'Delete Conversation',
                'Are you sure you want to delete this conversation?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.removeConversationFiles(currentItem)
                self.ui.TextBrowser.clear()
                if self.ui.ListWidget_Conversation.count() > 0:
                    self.LoadCurrentHistory(self.ui.ListWidget_Conversation.currentItem()) #self.ui.ListWidget_Conversation.click(self.ui.ListWidget_Conversation.currentItem())
                # Remove message
                self.MessagesDict.pop(old_name)

    def ShowContextMenu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Delete Conversation", self)
        delete_action.triggered.connect(self.deleteConversation)
        rename_action = QAction("Rename Conversation", self)
        rename_action.triggered.connect(self.renameConversation)
        context_menu.addActions([delete_action, rename_action])
        context_menu.exec(self.ui.ListWidget_Conversation.mapToGlobal(position))

    def LoadConversationList(self):
        # Check if the conversations directory exists
        if not os.path.exists(ConversationDir):
            os.makedirs(ConversationDir)
        # Check if the questions directory exists
        if not os.path.exists(QuestionDir):
            os.makedirs(QuestionDir)
        # Remove empty conversations(&questions) and add the rest to history list
        self.ui.ListWidget_Conversation.clear()
        for HistoryFileName in os.listdir(ConversationDir):
            if HistoryFileName.endswith('.txt'):
                HistoryFilePath = Path(ConversationDir).joinpath(HistoryFileName).as_posix()
                QuestionFilePath = Path(QuestionDir).joinpath(HistoryFileName).as_posix()
                if os.path.getsize(HistoryFilePath) == 0:
                    os.remove(HistoryFilePath)
                    os.remove(QuestionFilePath) if Path(QuestionFilePath).exists() else None
                    continue
                self.ui.ListWidget_Conversation.addItem(HistoryFileName[:-4]) # Remove the .txt extension

    def LoadCurrentHistory(self, item: QListWidgetItem):
        # Load a conversation from a txt file and display it in the browser
        self.ConversationFilePath = Path(ConversationDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.ConversationFilePath, 'r', encoding = 'utf-8') as f:
            Messages = [json.loads(line) for line in f]
        # Build&Set Markdown
        markdown = BuildMessageMarkdown(Messages)
        self.ui.TextBrowser.setText(markdown) #self.ui.TextBrowser.setMarkdown(markdown)
        # Load a question from the txt file and display it in the input area
        self.QuestionFilePath = Path(QuestionDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.QuestionFilePath, 'r', encoding = 'utf-8') as f:
            Question = f.read()
        # Set qustion
        self.ui.TextEdit_Input.setText(Question)

    def ClearConversations(self):
        listItems = [self.ui.ListWidget_Conversation.item(i) for i in range(self.ui.ListWidget_Conversation.count())]
        for listItem in listItems:
            self.removeConversationFiles(listItem)

    def CreateConversation(self):
        # Get the current time as the name of conversation
        beijing_timezone = pytz.timezone('Asia/Shanghai')
        formatted_time = datetime.now(beijing_timezone).strftime("%Y_%m_%d_%H_%M_%S")
        # Check if the path would be overwritten
        FilePath = Path(ConversationDir).joinpath(f"{formatted_time}.txt")
        Directory, FileName = os.path.split(FilePath)
        while Path(FilePath).exists():
            pattern = r'(\d+)\)\.'
            if re.search(pattern, FileName) is None:
                FileName = FileName.replace('.', '(0).')
            else:
                CurrentNumber = int(re.findall(pattern, FileName)[-1])
                FileName = FileName.replace(f'({CurrentNumber}).', f'({CurrentNumber + 1}).')
            FilePath = Path(Directory).joinpath(FileName).as_posix()
        FileName = Path(FilePath).name
        ConversationName = Path(FilePath).stem
        # Update the history file path and the question file path
        self.ConversationFilePath = FilePath
        self.QuestionFilePath = Path(QuestionDir).joinpath(FileName).as_posix()
        # Set the files & browser
        with open(self.ConversationFilePath, 'w', encoding = 'utf-8') as f:
            f.write('')
        self.ui.TextBrowser.clear()
        with open(self.QuestionFilePath, 'w', encoding = 'utf-8') as f:
            f.write('')
        self.ui.TextEdit_Input.clear()
        # Add the given name to the history list and select it
        NewConversation = QListWidgetItem(ConversationName)
        self.ui.ListWidget_Conversation.addItem(NewConversation)
        self.ui.ListWidget_Conversation.setCurrentItem(NewConversation)
        # Init message
        self.MessagesDict[ConversationName] = []
        self.applyRole()

    def saveConversation(self, Messages: list):
        with open(self.ConversationFilePath, 'w', encoding = 'utf-8') as f:
            ConversationStr = '\n'.join(json.dumps(message) for message in Messages)
            f.write(ConversationStr)

    def saveQuestion(self, Question: str):
        with open(self.QuestionFilePath, 'w', encoding = 'utf-8') as f:
            QuestionStr = Question.strip()
            f.write(QuestionStr)

    def LoadQuestions(self):
        ChildWindow_Test = TestWindow(self)
        ChildWindow_Test.exec()
        Questions =  ChildWindow_Test.QuestionList
        for Question in Questions:
            self.CreateConversation()
            self.ui.TextEdit_Input.setText(Question)
            #self.Query()

    def updateRecord(self, ConversationName):
        Messages = self.MessagesDict[ConversationName]
        # Build&Set Markdown
        markdown = BuildMessageMarkdown(Messages)
        self.ui.TextBrowser.setText(markdown) if self.ui.ListWidget_Conversation.currentItem().text() == ConversationName else None #self.ui.TextBrowser.setMarkdown(markdown)
        # Move the scrollbar to the bottom
        cursor = self.ui.TextBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.TextBrowser.setTextCursor(cursor)
        # Save the current conversation to a txt file with the given name
        self.saveConversation(Messages)

    def recieveAnswer(self, recievedText, ConversationName):
        Messages = self.MessagesDict[ConversationName]
        if Messages[-1]['role'] == 'user':
            Messages.append({'role': 'assistant', 'content': recievedText})
        '''
        else:
            Messages[-1]['content'] += recievedText
        '''
        self.MessagesDict[ConversationName] = Messages
        self.updateRecord(ConversationName)

    def startThread(self, InputContent, ConversationName, TestTimes = None):
        def blockList(block: bool):
            self.ui.ListWidget_Conversation.setEnabled(block)
            self.ui.Button_ClearConversations.setEnabled(block)
            self.ui.Button_CreateConversation.setEnabled(block)
            self.ui.Button_Load.setEnabled(block)
            self.ui.Button_Send.setEnabled(block)
            self.ui.Button_Test.setEnabled(block)
            self.ui.TextEdit_Input.blockKeyEnter(block)
        blockList(False)
        Messages = self.MessagesDict[ConversationName]
        if InputContent.strip().__len__() > 0:
            if self.thread is not None and self.thread.isRunning():
                self.thread.terminate()
                self.thread.wait()
            Messages.append({'role': 'user', 'content': InputContent})
            self.MessagesDict[ConversationName] = Messages
            self.updateRecord(ConversationName)
            self.thread = RequestThread(
                protocol = self.ui.ComboBox_Protocol.currentText(),
                ip = self.ui.LineEdit_ip.text(),
                port = self.ui.SpinBox_port.text(),
                type = self.ui.ComboBox_Type.currentText(),
                model = self.ui.ComboBox_Model.currentText(),
                messages = Messages,
                options = None,
                testtimes = TestTimes
            )
            self.thread.textReceived.connect(lambda text: self.recieveAnswer(text, ConversationName))
            self.thread.textReceived.connect(lambda: blockList(True))
            self.thread.start()

    def Query(self):
        InputContent = self.ui.TextEdit_Input.toPlainText()
        self.CreateConversation() if self.ui.ListWidget_Conversation.count() == 0 else None
        ConversationName = self.ui.ListWidget_Conversation.currentItem().text()
        self.startThread(InputContent, ConversationName)
        self.ui.TextEdit_Input.clear()
        self.ui.TextEdit_Input.setFocus()

    def QueryTest(self):
        InputContent = self.ui.TextEdit_Input.toPlainText()
        self.CreateConversation() if self.ui.ListWidget_Conversation.count() == 0 else None
        ConversationName = self.ui.ListWidget_Conversation.currentItem().text()
        TotalTestTimes, ok = QInputDialog.getText(self,
            'Set Testing Times',
            'Enter testing times:'
        )
        if ok and TotalTestTimes.strip().__len__() > 0:
            self.TotalTestTimes = int(TotalTestTimes.strip())
            if self.TotalTestTimes <= 0:
                MsgBox = QMessageBox()
                MsgBox.setWindowTitle('Warning')
                MsgBox.setText(f'Incorrect number!')
                MsgBox.exec()
                return
        else:
            return
        self.startThread(InputContent, ConversationName, TotalTestTimes)
        self.ui.TextEdit_Input.clear()
        self.ui.TextEdit_Input.setFocus()

    def ShutDown(self):
        exitRequest(
            protocol = self.ui.ComboBox_Protocol.currentText(),
            ip = self.ui.LineEdit_ip.text(),
            port = self.ui.SpinBox_port.text(),
        )

    def Main(self):
        # Chat - ParamsManager
        Path_Config_Chat = NormPath(Path(ConfigDir).joinpath('Config_Chat.ini'))
        ParamsManager_Chat = ParamsManager(Path_Config_Chat)

        '''
        self.setWindowTitle('PromptTest Client')
        self.setWindowIcon(QIcon(NormPath(Path(CurrentDir).joinpath('icon.png'))))
        '''

        # Theme toggler
        ComponentsSignals.Signal_SetTheme.connect(
            lambda: self.ui.CheckBox_SwitchTheme.setChecked(
                {Theme.Light: True, Theme.Dark: False}.get(EasyTheme.THEME)
            )
        )
        Function_ConfigureCheckBox(
            CheckBox = self.ui.CheckBox_SwitchTheme,
            CheckedEvents = [
                lambda: ParamsManager_Chat.Config.EditConfig('Settings', 'Theme', Theme.Light),
                lambda: ComponentsSignals.Signal_SetTheme.emit(Theme.Light) if EasyTheme.THEME != Theme.Light else None
            ],
            UncheckedEvents = [
                lambda: ParamsManager_Chat.Config.EditConfig('Settings', 'Theme', Theme.Dark),
                lambda: ComponentsSignals.Signal_SetTheme.emit(Theme.Dark) if EasyTheme.THEME != Theme.Dark else None
            ],
            TakeEffect = True
        )

        # Window controling buttons
        self.closed.connect(
            lambda: (
                self.ShutDown(),
                os._exit(0)
            )
        )
        self.ui.Button_Close_Window.clicked.connect(self.close)
        self.ui.Button_Maximize_Window.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized())
        self.ui.Button_Minimize_Window.clicked.connect(self.showMinimized)

        # Top area
        self.ui.ComboBox_Protocol.setToolTip("请选择协议")
        self.ui.ComboBox_Protocol.addItems(['http', 'https'])
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Protocol,
            Section = 'Input Params',
            Option = 'Protocol',
            DefaultValue = 'http'
        )

        self.ui.LineEdit_ip.setToolTip("请输入IP地址")
        ParamsManager_Chat.SetParam(
            Widget = self.ui.LineEdit_ip,
            Section = 'Input Params',
            Option = 'IP',
            DefaultValue = '127.0.0.1',
            SetPlaceholderText = True,
            PlaceholderText = "Please enter the ip"
        )

        self.ui.SpinBox_port.setToolTip("请输入端口号")
        self.ui.SpinBox_port.setRange(0, 65535)
        ParamsManager_Chat.SetParam(
            Widget = self.ui.SpinBox_port,
            Section = 'Input Params',
            Option = 'Port',
            DefaultValue = 8080
        )

        self.ui.ComboBox_Model.setToolTip("请选择模型")
        self.ui.ComboBox_Model.addItems(['gpt-4o', 'dall-e3'])
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Model,
            Section = 'Input Params',
            Option = 'Model',
            DefaultValue = 'gpt-4o'
        )

        '''
        self.ui.ComboBox_Role.setToolTip("请选择角色")
        self.ui.ComboBox_Role.addItems(list(self.roles.keys()))
        self.ui.ComboBox_Role.currentIndexChanged.connect(self.applyRole)
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Role,
            Section = 'Input Params',
            Option = 'Role',
            DefaultValue = "无"
        )
        '''

        self.ui.ComboBox_Type.setToolTip("请选择类型")
        self.ui.ComboBox_Type.addItems(['gpt', 'assistant'])
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Type,
            Section = 'Input Params',
            Option = 'Role',
            DefaultValue = "assistant"
        )

        # Right area
        self.ui.TextEdit_Input.textChanged.connect(self.saveQuestion)
        self.ui.TextEdit_Input.keyEnterPressed.connect(self.Query)
        self.ui.TextEdit_Input.setPlaceholderText(
            """
            请在此区域输入您的问题，点击 Send 或按下 Ctrl+Enter 发送提问
            如果只返回了问题而没有答案，请等待几秒或者换一个模型试试
            """
        )

        self.ui.Button_Load.clicked.connect(self.LoadQuestions)

        self.ui.Button_Send.clicked.connect(self.Query)

        self.ui.Button_Test.clicked.connect(self.QueryTest)

        # Left area
        self.ui.ListWidget_Conversation.itemClicked.connect(self.LoadCurrentHistory)
        self.ui.ListWidget_Conversation.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.ListWidget_Conversation.customContextMenuRequested.connect(self.ShowContextMenu)

        self.ui.Button_ClearConversations.clicked.connect(self.ClearConversations)

        self.ui.Button_CreateConversation.clicked.connect(self.CreateConversation)

        # Load histories
        self.LoadConversationList()

        # Create a new conversation
        self.CreateConversation()

        # Set the widget to be focused
        self.ui.TextEdit_Input.setFocus()

        # Show window
        self.show()


if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = MainWindow()
    window.Main()
    sys.exit(App.exec())