# -*- coding: utf-8 -*-

import os
import sys
import argparse
import json
import requests
import pytz
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtGui import QTextCursor, QAction, QStandardItem
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets import ComponentsSignals, Theme, EasyTheme, IconBase
from QEasyWidgets.Windows import MenuBase, InputDialogBase

from Functions import *
from windows.Windows import *
from config import CurrentDir, PromptDir, ConversationDir, QuestionDir, ConfigDir

##############################################################################################################################

# 启动参数解析，启动环境，应用端口由命令行传入
parser = argparse.ArgumentParser()
parser.add_argument("--promptdir",       help = "prompt目录", type = str, default = PromptDir)
parser.add_argument("--conversationdir", help = "对话目录",   type = str, default = ConversationDir)
parser.add_argument("--questiondir",     help = "问题目录",   type = str, default = QuestionDir)
parser.add_argument("--configdir",       help = "配置目录",   type = str, default = ConfigDir)
args = parser.parse_args()

PromptDir = args.promptdir
ConversationDir = args.conversationdir
QuestionDir = args.questiondir
ConfigDir = args.configdir

##############################################################################################################################

def BuildMessageMarkdown(messages: list[dict]):
    markdown = ""
    for message in messages:
        role = str(message['role']).strip()
        content = str(message['content']).strip()
        if len(content) == 0:
            continue
        content = QFunc.ToMarkdown(content)
        if role == 'user':
            markdown += f"**Q**:\n\n{content}\n\n\n"
        if role == 'assistant':
            markdown += f"**A**:\n\n{content}\n\n\n"
            markdown += "---------------------------------------\n\n\n"
    return markdown


def chatRequest(
    #env: str = 'uat',
    protocol: str = 'http',
    ip: str = 'localhost',
    port: Optional[int] = None,
    type: str = 'assistant',
    model: Optional[str] = None,
    code: Optional[str] = None,
    messages: list[dict] = [{}],
    options: Optional[dict] = None,
    testtimes: Optional[int] = None,
    stream: bool = True
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
        yield "Request failed", response.status_code

    # gpt/智能体接口请求
    if type == 'gpt':
        query = f"model={'gpt-4o' if model is None else model}{f'&testtimes={testtimes}' if testtimes is not None else ''}"
    if type == 'assistant':
        query = f"code={'114514' if code is None else code}{f'&testtimes={testtimes}' if testtimes is not None else ''}"
    URL = f"{protocol}://{ip}:{port}/{type}{f'?{query}' if len(query) > 0 else ''}"
    Headers = {
        'Authorization': oauth_token
    }
    Payload = {
        'message': messages,
        'options': options
    } if options is not None else {
        'message': messages
    }
    with requests.post(
        url = URL,
        headers = Headers,
        data = json.dumps(Payload),
        stream = stream
    ) as response:
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size = 1024 if stream else None, decode_unicode = False):
                if chunk:
                    content = chunk.decode('utf-8', errors = 'ignore')
                    try:
                        parsed_content = json.loads(content)
                        result = parsed_content['data']
                        yield result, response.status_code
                    except:
                        continue
        else:
            yield "Request failed", response.status_code


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
        code: Optional[str] = None,
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
        self.code = code
        self.messages = messages
        self.options = options
        self.testtimes = testtimes

    def run(self):
        for result, statuscode in chatRequest(
            #env = self.env,
            protocol = self.protocol,
            ip = self.ip,
            port = self.port,
            type = self.type,
            model = self.model,
            code = self.code,
            messages = self.messages,
            options = self.options,
            testtimes = self.testtimes
        ):
            self.textReceived.emit(str(result) if statuscode == 200 else "请求失败")

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

    def getRoles(self):
        # Check if the prompt directory exists
        if not os.path.exists(PromptDir):
            os.makedirs(PromptDir)
        # Initialize roles and add prompt to combobox
        for HistoryFileName in os.listdir(PromptDir):
            if HistoryFileName.endswith('.txt'):
                HistoryFilePath = Path(PromptDir).joinpath(HistoryFileName).as_posix()
                if os.path.getsize(HistoryFilePath) == 0:
                    os.remove(HistoryFilePath)
                    continue
                with open(HistoryFilePath, 'r', encoding = 'utf-8') as f:
                    Prompt = f.read()
                self.roles[HistoryFileName[:-4]] = Prompt
        return self.roles

    def applyRole(self):
        '''
        if self.ui.ComboBox_Role.count() != len(self.roles.keys()):
            return
        '''
        for ConversationName, Messages in self.MessagesDict.items():
            for Message in Messages.copy():
                Messages.remove(Message) if Message['role'] == 'system' else None
            Messages.append(
                {
                    'role': 'system',
                    'content': self.roles[self.ui.ComboBox_Role.currentText()]
                }
            )
            self.MessagesDict[ConversationName] = Messages

    def manageRole(self):
        ChildWindow_Prompt = PromptWindow(self, PromptDir)
        ChildWindow_Prompt.exec()
        # Update roles
        self.roles = {**{"无": ""}, **ChildWindow_Prompt.PromptDict}
        # Update combox and apply role
        SelectedRole = self.ui.ComboBox_Role.currentText()
        self.ui.ComboBox_Role.clear()
        self.ui.ComboBox_Role.addItems(list(self.roles.keys()))
        self.ui.ComboBox_Role.setCurrentText(SelectedRole) if SelectedRole in self.roles.keys() else None
        self.applyRole()

    def LoadHistories(self):
        # Check if the conversations directory exists
        if not os.path.exists(ConversationDir):
            os.makedirs(ConversationDir)
        # Check if the questions directory exists
        if not os.path.exists(QuestionDir):
            os.makedirs(QuestionDir)
        # Initialize MessagesDict and add conversations&questions to listwidget
        self.ui.ListWidget_Conversation.clear()
        for HistoryFileName in os.listdir(ConversationDir):
            if HistoryFileName.endswith('.txt'):
                ConversationFilePath = Path(ConversationDir).joinpath(HistoryFileName).as_posix()
                QuestionFilePath = Path(QuestionDir).joinpath(HistoryFileName).as_posix()
                if os.path.getsize(ConversationFilePath) == 0:
                    os.remove(ConversationFilePath)
                    os.remove(QuestionFilePath) if Path(QuestionFilePath).exists() else None
                    continue
                with open(ConversationFilePath, 'r', encoding = 'utf-8') as f:
                    Messages = [json.loads(Message) for Message in f.readlines()]
                self.MessagesDict[HistoryFileName[:-4]] = Messages # Remove the .txt extension
                self.ui.ListWidget_Conversation.addItem(HistoryFileName[:-4])

    def loadHistory(self, item: QStandardItem):
        # In case the conversation isn't selected
        self.ui.ListWidget_Conversation.setCurrentItem(item) if self.ui.ListWidget_Conversation.currentItem() != item else None
        # Load a conversation from a txt file and display it in the browser
        self.ConversationFilePath = Path(ConversationDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.ConversationFilePath, 'r', encoding = 'utf-8') as f:
            Messages = [json.loads(line) for line in f]
        # Build&Set Markdown
        markdown = BuildMessageMarkdown(Messages)
        self.ui.TextBrowser.setMarkdown(markdown)
        # Load a question from the txt file and display it in the input area
        self.QuestionFilePath = Path(QuestionDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.QuestionFilePath, 'r', encoding = 'utf-8') as f:
            Question = f.read()
        # Set qustion
        self.ui.TextEdit_Input.setText(Question)

    def removeHistoryFiles(self, listItem: QStandardItem):
        self.ui.ListWidget_Conversation.takeItem(self.ui.ListWidget_Conversation.row(listItem))
        os.remove(Path(ConversationDir).joinpath(listItem.text() + '.txt').as_posix())
        os.remove(Path(QuestionDir).joinpath(listItem.text() + '.txt').as_posix())

    def renameConversation(self):
        currentItem = self.ui.ListWidget_Conversation.currentItem()
        if currentItem is not None:
            old_name = currentItem.text()
            new_name, ok = InputDialogBase.getText(self,
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
                self.MessagesDict.pop(old_name) # Remove message
                self.applyRole()

    def deleteConversation(self):
        currentItem = self.ui.ListWidget_Conversation.currentItem()
        if currentItem is not None:
            old_name = currentItem.text()
            confirm = MessageBoxBase.pop(self,
                QMessageBox.Question,
                'Delete Conversation',
                'Sure you wanna delete this conversation?',
                QMessageBox.Yes | QMessageBox.No,
            )
            if confirm == QMessageBox.Yes:
                self.removeHistoryFiles(currentItem) # Remove file
                self.ui.TextBrowser.clear()
                if self.ui.ListWidget_Conversation.count() > 0:
                    self.loadHistory(self.ui.ListWidget_Conversation.currentItem())
                self.MessagesDict.pop(old_name) # Remove message

    def createConversation(self):
        # Get the current time as the name of conversation
        beijing_timezone = pytz.timezone('Asia/Shanghai')
        formatted_time = datetime.now(beijing_timezone).strftime("%Y_%m_%d_%H_%M_%S")
        # Check if the path would be overwritten
        FilePath = Path(ConversationDir).joinpath(f"{formatted_time}.txt")
        FilePath = QFunc.RenameFile(FilePath)
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
        NewConversation = QStandardItem(ConversationName)
        self.ui.ListWidget_Conversation.addItem(NewConversation)
        self.ui.ListWidget_Conversation.setCurrentItem(NewConversation)
        # Init message
        self.MessagesDict[ConversationName] = []
        self.applyRole()
        # Set focus to input box
        self.ui.TextEdit_Input.setFocus()

    def ShowContextMenu(self, position):
        context_menu = MenuBase(self)
        delete_action = QAction("Delete Conversation", self)
        delete_action.triggered.connect(self.deleteConversation)
        rename_action = QAction("Rename Conversation", self)
        rename_action.triggered.connect(self.renameConversation)
        context_menu.addActions([delete_action, rename_action])
        context_menu.exec(self.ui.ListWidget_Conversation.mapToGlobal(position))

    def ClearConversations(self):
        listItems = [self.ui.ListWidget_Conversation.item(i) for i in range(self.ui.ListWidget_Conversation.count())]
        for listItem in listItems:
            self.removeHistoryFiles(listItem) # Remove file
            self.MessagesDict.pop(listItem.text()) # Remove message
        self.ui.TextBrowser.clear()

    def saveConversation(self, Messages: list):
        if self.ui.ListWidget_Conversation.count() == 0:
            return
        with open(self.ConversationFilePath, 'w', encoding = 'utf-8') as f:
            ConversationStr = '\n'.join(json.dumps(message) for message in Messages)
            f.write(ConversationStr)

    def saveQuestion(self, Question: str):
        if self.ui.ListWidget_Conversation.count() == 0:
            return
        with open(self.QuestionFilePath, 'w', encoding = 'utf-8') as f:
            QuestionStr = Question.strip()
            f.write(QuestionStr)

    def updateRecord(self, ConversationName):
        Messages = self.MessagesDict[ConversationName]
        # Build&Set Markdown
        markdown = BuildMessageMarkdown(Messages)
        self.ui.TextBrowser.setMarkdown(markdown) if self.ui.ListWidget_Conversation.currentItem().text() == ConversationName else None
        # Move the scrollbar to the bottom
        cursor = self.ui.TextBrowser.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.TextBrowser.setTextCursor(cursor)
        # Save the current conversation to a txt file with the given name
        self.saveConversation(Messages)

    def recieveAnswer(self, recievedText, ConversationName):
        Messages = self.MessagesDict[ConversationName]
        if Messages[-1]['role'] == 'assistant':
            Messages[-1]['content'] += recievedText
        if Messages[-1]['role'] == 'user':
            Messages.append({'role': 'assistant', 'content': recievedText})
        self.MessagesDict[ConversationName] = Messages
        self.updateRecord(ConversationName)

    def startThread(self, InputContent: str, ConversationName: str, TestTimes: Optional[int] = None):
        def blockList(block: bool):
            self.ui.ComboBox_Protocol.setEnabled(block)
            self.ui.LineEdit_ip.setEnabled(block)
            self.ui.SpinBox_port.setEnabled(block)
            self.ui.ComboBox_Type.setEnabled(block)
            self.ui.ComboBox_Model.setEnabled(block)
            self.ui.ComboBox_Role.setEnabled(block)
            self.ui.Button_ManageRole.setEnabled(block)
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
                code = self.ui.LineEdit_AssistantID.text(),
                messages = Messages,
                options = None,
                testtimes = TestTimes
            )
            self.thread.textReceived.connect(lambda text: self.recieveAnswer(text, ConversationName))
            self.thread.textReceived.connect(lambda: blockList(True))
            self.thread.start()

    def Query(self):
        InputContent = self.ui.TextEdit_Input.toPlainText()
        self.createConversation() if self.ui.ListWidget_Conversation.count() == 0 else None
        ConversationName = self.ui.ListWidget_Conversation.currentItem().text()
        self.startThread(InputContent, ConversationName)
        self.ui.TextEdit_Input.clear()
        self.ui.TextEdit_Input.setFocus()

    def QueryTest(self):
        InputContent = self.ui.TextEdit_Input.toPlainText()
        self.createConversation() if self.ui.ListWidget_Conversation.count() == 0 else None
        ConversationName = self.ui.ListWidget_Conversation.currentItem().text()
        TotalTestTimes, ok = InputDialogBase.getText(self,
            'Set Testing Times',
            'Enter testing times:'
        )
        if ok and TotalTestTimes.strip().__len__() > 0:
            self.TotalTestTimes = int(TotalTestTimes.strip())
            if self.TotalTestTimes <= 0:
                Function_ShowMessageBox(self,
                    QMessageBox.Warning,
                    'Warning',
                    'Incorrect number!'
                )
                return
        else:
            return
        self.startThread(InputContent, ConversationName, int(TotalTestTimes))
        self.ui.TextEdit_Input.clear()
        self.ui.TextEdit_Input.setFocus()

    def LoadQuestions(self):
        ChildWindow_Test = TestWindow(self)
        ChildWindow_Test.exec()
        Questions =  ChildWindow_Test.QuestionList
        for Question in Questions:
            self.createConversation()
            self.ui.TextEdit_Input.setText(Question)

    def ExitRequest(self):
        exitRequest(
            protocol = self.ui.ComboBox_Protocol.currentText(),
            ip = self.ui.LineEdit_ip.text(),
            port = self.ui.SpinBox_port.text(),
        )

    def Main(self):
        # Chat - ParamsManager
        Path_Config_Chat = QFunc.NormPath(Path(ConfigDir).joinpath('Config_Chat.ini'))
        ParamsManager_Chat = ParamsManager(Path_Config_Chat)

        # Logo
        self.setWindowIcon(QIcon(QFunc.NormPath(Path(CurrentDir).joinpath('assets/images/Logo.ico'))))

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
            TakeEffect = False
        )

        # Window controling buttons
        self.closed.connect(
            lambda: (
                #self.ExitRequest(),
                os._exit(0)
            )
        )
        self.ui.Button_Close_Window.clicked.connect(self.close)
        self.ui.Button_Close_Window.ClearDefaultStyleSheet()
        self.ui.Button_Close_Window.setStyleSheet(
            "ButtonBase {background-color: transparent; border: none;}"
            "ButtonBase:hover {background-color: rgba(210, 123, 123, 210);}"
        )
        self.ui.Button_Close_Window.setIcon(IconBase.X)

        self.ui.Button_Maximize_Window.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized())
        self.ui.Button_Maximize_Window.ClearDefaultStyleSheet()
        self.ui.Button_Maximize_Window.setStyleSheet(
            "ButtonBase {background-color: transparent; border: none;}"
            "ButtonBase:hover {background-color: rgba(123, 123, 123, 123);}"
        )
        self.ui.Button_Maximize_Window.setIcon(IconBase.FullScreen)

        self.ui.Button_Minimize_Window.clicked.connect(self.showMinimized)
        self.ui.Button_Minimize_Window.ClearDefaultStyleSheet()
        self.ui.Button_Minimize_Window.setStyleSheet(
            "ButtonBase {background-color: transparent; border: none;}"
            "ButtonBase:hover {background-color: rgba(123, 123, 123, 123);}"
        )
        self.ui.Button_Minimize_Window.setIcon(IconBase.Dash)

        # Top area
        self.ui.ToolBox.widget(0).setText(QCA.translate("ToolBox", "参数配置"))
        #self.ui.ToolBox.widget(0).collapse()

        self.ui.Label_Protocal.setText("协议")
        self.ui.ComboBox_Protocol.addItems(['http', 'https'])
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Protocol,
            Section = 'Input Params',
            Option = 'Protocol',
            DefaultValue = 'http'
        )

        self.ui.Label_ip.setText("地址")
        self.ui.LineEdit_ip.RemoveFileDialogButton()
        ParamsManager_Chat.SetParam(
            Widget = self.ui.LineEdit_ip,
            Section = 'Input Params',
            Option = 'IP',
            DefaultValue = '127.0.0.1',
            SetPlaceholderText = True,
            PlaceholderText = "Please enter the ip"
        )

        self.ui.Label_port.setText("端口")
        self.ui.SpinBox_port.setRange(0, 65535)
        ParamsManager_Chat.SetParam(
            Widget = self.ui.SpinBox_port,
            Section = 'Input Params',
            Option = 'Port',
            DefaultValue = 8080
        )

        self.ui.Label_Type.setText("类型")
        self.ui.ComboBox_Type.addItems(['gpt', 'assistant'])
        self.ui.ComboBox_Type.currentTextChanged.connect(
            lambda Text: (
                self.ui.StackedWidget_TypeParams.setCurrentIndex(0 if Text == 'gpt' else 1),
            )
        )
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Type,
            Section = 'Input Params',
            Option = 'Role',
            DefaultValue = "gpt"
        )

        self.ui.Label_Model.setText("模型")
        self.ui.ComboBox_Model.addItems(['gpt-4o', 'gemini-1.5-pro-001', 'dall-e3'])
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Model,
            Section = 'Input Params',
            Option = 'Model',
            DefaultValue = 'gpt-4o'
        )

        self.ui.Label_Role.setText("角色")
        self.ui.ComboBox_Role.addItems(list(self.getRoles().keys()))
        self.ui.ComboBox_Role.activated.connect(self.applyRole)
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Role,
            Section = 'Input Params',
            Option = 'Role',
            DefaultValue = "无"
        )

        self.ui.Label_AssistantID.setText("ID")
        self.ui.LineEdit_AssistantID.RemoveFileDialogButton()
        ParamsManager_Chat.SetParam(
            Widget = self.ui.LineEdit_AssistantID,
            Section = 'Input Params',
            Option = 'AssistantID',
            DefaultValue = '6b16892979c2487ba5817377e5722acd',
            SetPlaceholderText = True,
            PlaceholderText = "Please enter the assistant's ID"
        )

        self.ui.Button_ManageRole.setText("")
        self.ui.Button_ManageRole.setToolTip("管理角色")
        self.ui.Button_ManageRole.setIcon(IconBase.Ellipsis)
        self.ui.Button_ManageRole.clicked.connect(self.manageRole)

        # Right area
        self.ui.TextEdit_Input.textChanged.connect(self.saveQuestion)
        self.ui.TextEdit_Input.keyEnterPressed.connect(self.Query)
        self.ui.TextEdit_Input.setPlaceholderText(
            """
            请在此区域输入您的问题，点击 Send 或按下 Ctrl+Enter 发送提问
            如果只返回了问题而没有答案，请等待几秒或者换一个模型试试
            """
        )

        self.ui.Button_Load.setText('从文件导入问题')
        self.ui.Button_Load.clicked.connect(self.LoadQuestions)

        self.ui.Button_Send.setText('发送')
        self.ui.Button_Send.clicked.connect(self.Query)

        self.ui.Button_Test.setText('测试')
        self.ui.Button_Test.clicked.connect(self.QueryTest)

        # Left area
        self.ui.ListWidget_Conversation.itemClicked.connect(self.loadHistory)
        self.ui.ListWidget_Conversation.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.ListWidget_Conversation.customContextMenuRequested.connect(self.ShowContextMenu)

        self.ui.Button_ClearConversations.setText('清空对话')
        self.ui.Button_ClearConversations.clicked.connect(self.ClearConversations)

        self.ui.Button_CreateConversation.setText('创建对话')
        self.ui.Button_CreateConversation.clicked.connect(self.createConversation)

        # Load histories
        self.LoadHistories()

        # Set Theme
        ComponentsSignals.Signal_SetTheme.emit(ParamsManager_Chat.Config.GetValue('Settings', 'Theme', Theme.Auto))

        # Show window
        self.show()

        # Create a new conversation while there is no history conversation
        self.createConversation() if self.ui.ListWidget_Conversation.count() == 0 else self.loadHistory(self.ui.ListWidget_Conversation.item(0))

        # Apply role
        self.applyRole()

        # Set focus to input box
        self.ui.TextEdit_Input.setFocus()


if __name__ == '__main__':
    App = QApplication(sys.argv)

    SC = QSplashScreen(QPixmap(QFunc.NormPath(Path(CurrentDir).joinpath('assets/images/others/SplashScreen.png'))))
    SC.show()

    window = MainWindow()
    window.Main()

    sys.exit(App.exec())