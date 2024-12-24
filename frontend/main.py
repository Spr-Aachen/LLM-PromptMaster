# -*- coding: utf-8 -*-

import os
import sys
import argparse
import json
import json_repair
import time
import requests
import pytz
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QSettings
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtGui import QTextCursor, QAction, QStandardItem
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets import ComponentsSignals, Theme, EasyTheme, IconBase, Status
from QEasyWidgets.Windows import InputDialogBase
from QEasyWidgets.Components import MenuBase

from functions import *
from windows import *
from config import currentDir

##############################################################################################################################

# 启动参数解析，启动环境，应用端口由命令行传入
parser = argparse.ArgumentParser()
parser.add_argument("--host", help = "主机地址",   type = str, default = "localhost")
parser.add_argument("--port", help = "端口",       type = int, default = 8080)
parser.add_argument("--profiledir", help = "配置目录", type = str, default = Path(currentDir).joinpath('Profile').as_posix())
args = parser.parse_args()

profileDir = args.profiledir
promptDir = Path(profileDir).joinpath('Prompts').as_posix()
conversationDir = Path(profileDir).joinpath('Conversations').as_posix()
questionDir = Path(profileDir).joinpath('Questions').as_posix()
configDir = Path(profileDir).joinpath('Config').as_posix()

##############################################################################################################################

def chatRequest(
    #env: str = 'uat',
    sourceName: str = 'azure',
    env: Optional[str] = None,
    type: str = 'gpt',
    model: Optional[str] = None,
    code: Optional[str] = None,
    messages: list[dict] = [{}],
    options: Optional[dict] = None,
    testtimes: Optional[int] = None,
    stream: bool = True
):
    # Check connection
    try:
        response = requests.get(
            url = f"http://{args.host}:{args.port}/"
        )
    except Exception as e:
        yield str(e), 404
        return

    # Get token
    Headers = {
        'P-Rtoken': "...",
        'P-Auth': "...",
        "P-AppId": "..."
    }
    response = requests.get(
        url = f"http://{args.host}:{args.port}/auth",
        headers = Headers
    )
    if response.status_code == 200:
        res_token = response.json()
        Token = res_token.get("data", {})
        oAuth_token = f"Bearer {Token}"
    else:
        oAuth_token = ""
        yield "Request failed", response.status_code

    # Post message
    if type == 'gpt':
        query = f"source={sourceName}{f'&env={env}' if env is not None else ''}&model={'gpt-4o' if model is None else model}{f'&testtimes={testtimes}' if testtimes is not None else ''}"
    if type == 'assistant':
        query = f"source={sourceName}{f'&env={env}' if env is not None else ''}&code={'114514' if code is None else code}{f'&testtimes={testtimes}' if testtimes is not None else ''}"
    URL = f"http://{args.host}:{args.port}/{type}{f'?{query}' if len(query) > 0 else ''}"
    Headers = {
        'Authorization': oAuth_token
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
                        parsed_content = json_repair.loads(content)
                        result = parsed_content['data']
                        yield result, response.status_code
                    except:
                        continue
        else:
            yield "Request failed", response.status_code


def delRequest(
    
):
    ''''''


def exitService():
    with requests.post(
        url = f"http://{args.host}:{args.port}/shutdown"
    ) as response:
        return True if response.status_code == 200 else False

##############################################################################################################################

class thread_request(QThread):
    textReceived = Signal(str)

    def __init__(self,
        sourceName: str = 'azure',
        env: Optional[str] = None,
        type: str = 'gpt',
        model: Optional[str] = None,
        code: Optional[str] = None,
        messages: list[dict] = [{}],
        options: Optional[dict] = None,
        testtimes: Optional[int] = None
    ):
        super().__init__()

        self.sourceName = sourceName
        self.env = env
        self.type = type
        self.model = model
        self.code = code
        self.messages = messages
        self.options = options
        self.testtimes = testtimes

    def run(self):
        for result, statuscode in chatRequest(
            sourceName = self.sourceName,
            env = self.env,
            type = self.type,
            model = self.model,
            code = self.code,
            messages = self.messages,
            options = self.options,
            testtimes = self.testtimes
        ):
            self.textReceived.emit(result)
            time.sleep(0.03)

##############################################################################################################################

class MainWindow(Window_MainWindow):
    roles = {"无": ""}

    MessagesDict = {}

    Thread = None

    def __init__(self):
        super().__init__()

        self.centralWidget().deleteLater()

        self.setDockNestingEnabled(True)

        self.resize(900, 600)

        self.settings = QSettings(self)

    def closeEvent(self, event):
        self.exitService()
        QApplication.instance().exit()

    def getRoles(self):
        # Check if the prompt directory exists
        if not os.path.exists(promptDir):
            os.makedirs(promptDir)
        # Initialize roles and add prompt to combobox
        for HistoryFileName in os.listdir(promptDir):
            if HistoryFileName.endswith('.txt'):
                HistoryFilePath = Path(promptDir).joinpath(HistoryFileName).as_posix()
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
        ChildWindow_Prompt = PromptWindow(self, promptDir)
        ChildWindow_Prompt.exec()
        # Update roles
        self.roles = {**{"无": ""}, **ChildWindow_Prompt.PromptDict}
        # Update combox and apply role
        SelectedRole = self.ui.ComboBox_Role.currentText()
        self.ui.ComboBox_Role.clear()
        self.ui.ComboBox_Role.addItems(list(self.roles.keys()))
        self.ui.ComboBox_Role.setCurrentText(SelectedRole) if SelectedRole in self.roles.keys() else None
        self.applyRole()

    def loadHistories(self):
        # Check if the conversations directory exists
        if not os.path.exists(conversationDir):
            os.makedirs(conversationDir)
        # Check if the questions directory exists
        if not os.path.exists(questionDir):
            os.makedirs(questionDir)
        # Initialize MessagesDict and add conversations&questions to listwidget
        self.ui.ListWidget_Conversation.clear()
        for HistoryFileName in os.listdir(conversationDir):
            if HistoryFileName.endswith('.txt'):
                ConversationFilePath = Path(conversationDir).joinpath(HistoryFileName).as_posix()
                QuestionFilePath = Path(questionDir).joinpath(HistoryFileName).as_posix()
                if os.path.getsize(ConversationFilePath) == 0:
                    os.remove(ConversationFilePath)
                    os.remove(QuestionFilePath) if Path(QuestionFilePath).exists() else None
                    continue
                with open(ConversationFilePath, 'r', encoding = 'utf-8') as f:
                    Messages = [json.loads(Message) for Message in f.readlines()]
                self.MessagesDict[HistoryFileName[:-4]] = Messages # Remove the .txt extension
                self.ui.ListWidget_Conversation.addItem(HistoryFileName[:-4])

    def setMessages(self, messages: list[dict]):
        Messages = []
        for message in messages:
            Message = {}
            role = str(message['role']).strip()
            content = str(message['content']).strip()
            if len(content) == 0:
                continue
            content = QFunc.toMarkdown(content)
            Message[role] = content
            Messages.append(Message)
        self.ui.MessageBrowser.setMessages(
            [[list(Message.values())[0], True if list(Message.keys())[0] == 'user' else False, None] for Message in Messages]
        )

    def loadHistory(self, item: QStandardItem):
        # In case the conversation isn't selected
        self.ui.ListWidget_Conversation.setCurrentItem(item) if self.ui.ListWidget_Conversation.currentItem() != item else None
        # Load a conversation from a txt file and display it in the browser
        self.ConversationFilePath = Path(conversationDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.ConversationFilePath, 'r', encoding = 'utf-8') as f:
            Messages = [json.loads(line) for line in f]
        # Set messages
        self.setMessages(Messages)
        # Load a question from the txt file and display it in the input area
        self.QuestionFilePath = Path(questionDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.QuestionFilePath, 'r', encoding = 'utf-8') as f:
            Question = f.read()
        # Set qustion
        self.ui.TextEdit_Input.setText(Question)

    def removeHistoryFiles(self, listItem: QStandardItem):
        self.ui.ListWidget_Conversation.takeItem(self.ui.ListWidget_Conversation.row(listItem))
        os.remove(Path(conversationDir).joinpath(listItem.text() + '.txt').as_posix())
        os.remove(Path(questionDir).joinpath(listItem.text() + '.txt').as_posix())

    def renameConversation(self):
        currentItem = self.ui.ListWidget_Conversation.currentItem()
        if currentItem is not None:
            old_name = currentItem.text()
            new_name, ok = InputDialogBase.getText(self,
                'Rename Conversation',
                'Enter new conversation name:'
            )
            if ok and new_name:
                self.ConversationFilePath = Path(conversationDir).joinpath(f"{new_name}.txt").as_posix()
                os.rename(Path(conversationDir).joinpath(f"{old_name}.txt"), self.ConversationFilePath)
                currentItem.setText(new_name)
                self.QuestionFilePath = Path(questionDir).joinpath(f"{new_name}.txt").as_posix()
                os.rename(Path(questionDir).joinpath(f"{old_name}.txt"), self.QuestionFilePath)
                # Transfer&Remove message
                self.MessagesDict[new_name] = self.MessagesDict[old_name]
                self.MessagesDict.pop(old_name) # Remove message
                self.applyRole()

    def deleteConversation(self):
        currentItem = self.ui.ListWidget_Conversation.currentItem()
        if currentItem is not None:
            old_name = currentItem.text()
            confirm = MessageBoxBase.pop(self,
                QMessageBox.Question, 'Delete Conversation',
                text = 'Sure you wanna delete this conversation?',
                buttons = QMessageBox.Yes | QMessageBox.No,
            )
            if confirm == QMessageBox.Yes:
                self.removeHistoryFiles(currentItem) # Remove file
                self.ui.MessageBrowser.clear()
                if self.ui.ListWidget_Conversation.count() > 0:
                    self.loadHistory(self.ui.ListWidget_Conversation.currentItem())
                self.MessagesDict.pop(old_name) # Remove message

    def createConversation(self):
        # Get the current time as the name of conversation
        beijing_timezone = pytz.timezone('Asia/Shanghai')
        formatted_time = datetime.now(beijing_timezone).strftime("%Y_%m_%d_%H_%M_%S")
        # Check if the path would be overwritten
        FilePath = Path(conversationDir).joinpath(f"{formatted_time}.txt")
        FilePath = QFunc.renameIfExists(FilePath)
        FileName = Path(FilePath).name
        ConversationName = Path(FilePath).stem
        # Update the history file path and the question file path
        self.ConversationFilePath = FilePath
        self.QuestionFilePath = Path(questionDir).joinpath(FileName).as_posix()
        # Set the files & browser
        with open(self.ConversationFilePath, 'w', encoding = 'utf-8') as f:
            f.write('')
        self.ui.MessageBrowser.clear()
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

    def clearConversations(self):
        listItems = [self.ui.ListWidget_Conversation.item(i) for i in range(self.ui.ListWidget_Conversation.count())]
        for listItem in listItems:
            self.removeHistoryFiles(listItem) # Remove file
            self.MessagesDict.pop(listItem.text()) # Remove message
        self.ui.MessageBrowser.clear()

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

    def addMessage(self, currentRole: str, messages: list[dict], status = None):
        if status is not None:
            self.ui.MessageBrowser.addMessage(
                '', False, status, False
            )
            return
        for message in reversed(messages):
            role = str(message['role']).strip()
            content = str(message['content']).strip()
            if role != currentRole or len(content) == 0:
                continue
            content = QFunc.toMarkdown(content)
            self.ui.MessageBrowser.addMessage(
                content,
                isSent = False if currentRole == 'assistant' else True,
                status = status,
                stream = True if currentRole == 'assistant' else False,
            )
            break

    def recieveAnswer(self, recievedText, ConversationName):
        Messages = self.MessagesDict[ConversationName]
        if Messages[-1]['role'] == 'assistant':
            Messages[-1]['content'] += recievedText
        if Messages[-1]['role'] == 'user':
            Messages.append({'role': 'assistant', 'content': recievedText})
        self.MessagesDict[ConversationName] = Messages
        # Save the current conversation to a txt file with the given name
        self.saveConversation(Messages)
        # Update assistant message
        self.addMessage('assistant', Messages) if self.ui.ListWidget_Conversation.currentItem().text() == ConversationName else None

    def startThread(self, TestTimes: Optional[int] = None):
        InputContent = self.ui.TextEdit_Input.toPlainText()
        if InputContent.strip().__len__() == 0:
            return
        self.createConversation() if self.ui.ListWidget_Conversation.count() == 0 else None
        ConversationName = self.ui.ListWidget_Conversation.currentItem().text()
        def blockInput(block: bool):
            self.ui.ComboBox_Type.setDisabled(block)
            self.ui.ComboBox_Model.setDisabled(block)
            self.ui.ComboBox_Role.setDisabled(block)
            self.ui.Button_ManageRole.setDisabled(block)
            self.ui.ListWidget_Conversation.setDisabled(block)
            self.ui.Button_ClearConversations.setDisabled(block)
            self.ui.Button_CreateConversation.setDisabled(block)
            self.ui.Button_Load.setDisabled(block)
            self.ui.Button_Send.setDisabled(block)
            self.ui.Button_Test.setDisabled(block)
            self.ui.TextEdit_Input.blockKeyEnter(block)
        blockInput(True)
        Messages = self.MessagesDict[ConversationName]
        if self.Thread is not None and self.Thread.isRunning():
            self.Thread.terminate()
        Messages.append({'role': 'user', 'content': InputContent})
        self.MessagesDict[ConversationName] = Messages
        # Save the current conversation to a txt file with the given name
        self.saveConversation(Messages)
        # Update user message
        self.addMessage('user', Messages) if self.ui.ListWidget_Conversation.currentItem().text() == ConversationName else None
        # Start a new thread to send the request
        self.Thread = thread_request(
            sourceName = self.ui.ComboBox_Source.currentText(),
            env = None, #env = self.ui.ComboBox_Env.currentText(),
            type = self.ui.ComboBox_Type.currentText(),
            model = self.ui.ComboBox_Model.currentText(),
            code = self.ui.LineEdit_AssistantID.text(),
            messages = Messages,
            options = None,
            testtimes = TestTimes
        )
        self.Thread.textReceived.connect(
            lambda text: (
                self.recieveAnswer(text, ConversationName),
                Function_AnimateStackedWidget(
                    self.ui.StackedWidget_SendAndStop,
                    self.ui.StackedWidgetPage_Send
                ),
                blockInput(False)
            )
        )
        self.Thread.start()
        self.addMessage('', False, Status.Loading)
        self.ui.TextEdit_Input.clear()
        self.ui.TextEdit_Input.setFocus()
        Function_AnimateStackedWidget(
            self.ui.StackedWidget_SendAndStop,
            self.ui.StackedWidgetPage_Stop
        )

    def query(self):
        self.startThread()

    def queryTest(self):
        TotalTestTimes, ok = InputDialogBase.getText(self,
            'Set Testing Times',
            'Enter testing times:'
        )
        if ok and TotalTestTimes.strip().__len__() > 0:
            self.TotalTestTimes = int(TotalTestTimes.strip())
            if self.TotalTestTimes <= 0:
                MessageBoxBase.pop(self,
                    QMessageBox.Warning, 'Warning',
                    'Incorrect number!'
                )
                return
        else:
            return
        self.startThread(int(TotalTestTimes))

    def loadQuestions(self):
        ChildWindow_Test = TestWindow(self)
        ChildWindow_Test.exec()
        Questions =  ChildWindow_Test.QuestionList
        for Question in Questions:
            self.createConversation()
            self.ui.TextEdit_Input.setText(Question)

    def exitService(self):
        exitService()

    def stopService(self):
        if self.Thread is not None and self.Thread.isRunning():
            self.Thread.terminate()
        Function_AnimateStackedWidget(
            self.ui.StackedWidget_SendAndStop,
            self.ui.StackedWidgetPage_Send
        )

    def main(self):
        # Chat - ParamsManager
        Path_Config_Chat = QFunc.normPath(Path(configDir).joinpath('Config_Chat.ini'))
        ParamsManager_Chat = ParamsManager(Path_Config_Chat)

        # Logo
        self.setWindowIcon(QIcon(QFunc.normPath(Path(currentDir).joinpath('assets/images/Logo.ico'))))

        # Theme toggler
        # ComponentsSignals.Signal_SetTheme.connect(
        #     lambda: self.ui.CheckBox_SwitchTheme.setChecked(
        #         {Theme.Light: True, Theme.Dark: False}.get(EasyTheme.THEME)
        #     )
        # )
        # Function_ConfigureCheckBox(
        #     checkBox = self.ui.CheckBox_SwitchTheme,
        #     checkedEvents = [
        #         lambda: ParamsManager_Chat.config.editConfig('Settings', 'Theme', Theme.Light),
        #         lambda: ComponentsSignals.Signal_SetTheme.emit(Theme.Light) if EasyTheme.THEME != Theme.Light else None
        #     ],
        #     uncheckedEvents = [
        #         lambda: ParamsManager_Chat.config.editConfig('Settings', 'Theme', Theme.Dark),
        #         lambda: ComponentsSignals.Signal_SetTheme.emit(Theme.Dark) if EasyTheme.THEME != Theme.Dark else None
        #     ],
        #     takeEffect = False
        # )

        # Actions
        action_ResetLayout = QAction(QCA.translate("Action", "重置布局"), self)
        action_ResetLayout.triggered.connect(lambda: QFunc.resetLayout(self, self.settings))

        # MenuBar
        menuButton_Layout = QMenu(QCA.translate("Menu", "布局"))
        menuButton_Layout.addAction(action_ResetLayout)

        menuButton_Help = QMenu(QCA.translate("Menu", "帮助"))

        menuBar = QMenuBar()
        menuBar.addMenu(menuButton_Layout)
        menuBar.addSeparator()
        menuBar.addMenu(menuButton_Help)
        menuBar.addSeparator()
        menuBar.setFixedWidth(menuButton_Layout.sizeHint().width() + menuButton_Help.sizeHint().width())
        self.setMenuBar(menuBar)

        # Top area
        self.ui.dockWidget_Top.setFeatures(QDockWidget.DockWidgetMovable)
        self.ui.dockWidget_Top.setFixedHeight(self.ui.groupBox_Settings.minimumSizeHint().height())

        self.ui.groupBox_Settings.setTitle(QCA.translate("GroupBox", "设置"))

        self.ui.Label_Source.setText("来源")
        self.ui.ComboBox_Source.addItems(['openai', 'azure', 'transsion'])
        ParamsManager_Chat.SetParam(
            widget = self.ui.ComboBox_Source,
            section = 'Input Params',
            option = 'Source',
            defaultValue = 'azure'
        )

        self.ui.Label_Type.setText("类型")
        self.ui.ComboBox_Type.addItems(['gpt', 'assistant'])
        self.ui.ComboBox_Type.currentTextChanged.connect(
            lambda Text: (
                self.ui.StackedWidget_TypeParams.setCurrentIndex(0 if Text == 'gpt' else 1),
            )
        )
        ParamsManager_Chat.SetParam(
            widget = self.ui.ComboBox_Type,
            section = 'Input Params',
            option = 'Role',
            defaultValue = "gpt"
        )

        self.ui.Label_Model.setText("模型")
        self.ui.ComboBox_Model.addItems(['gpt-4o', 'gemini-1.5-pro-001', 'moonshot-v1-128k', 'claude-3-5-sonnet@20240620', 'dall-e3'])
        ParamsManager_Chat.SetParam(
            widget = self.ui.ComboBox_Model,
            section = 'Input Params',
            option = 'Model',
            defaultValue = 'gpt-4o'
        )

        self.ui.Label_Role.setText("角色")
        self.ui.ComboBox_Role.addItems(list(self.getRoles().keys()))
        self.ui.ComboBox_Role.activated.connect(self.applyRole)
        ParamsManager_Chat.SetParam(
            widget = self.ui.ComboBox_Role,
            section = 'Input Params',
            option = 'Role',
            defaultValue = "无"
        )
        self.ui.Button_ManageRole.setText("")
        self.ui.Button_ManageRole.setToolTip("管理角色")
        self.ui.Button_ManageRole.setIcon(IconBase.Ellipsis)
        self.ui.Button_ManageRole.clicked.connect(self.manageRole)

        self.ui.Label_AssistantID.setText("ID")
        ParamsManager_Chat.SetParam(
            widget = self.ui.LineEdit_AssistantID,
            section = 'Input Params',
            option = 'AssistantID',
            defaultValue = '6b16892979c2487ba5817377e5722acd',
            setPlaceholderText = True,
            placeholderText = "Please enter the assistant's ID"
        )

        self.ui.toolBox_AdvanceSettings.widget(0).setText(QCA.translate("ToolBox", "高级设置"))
        self.ui.toolBox_AdvanceSettings.widget(0).collapse()

        # Right area
        self.ui.dockWidget_Right.setFeatures(QDockWidget.DockWidgetMovable)

        self.ui.splitter.setStretchFactor(0, 1)

        self.ui.TextEdit_Input.textChanged.connect(lambda: self.saveQuestion(self.ui.TextEdit_Input.toPlainText()))
        self.ui.TextEdit_Input.keyEnterPressed.connect(self.query)
        self.ui.TextEdit_Input.setPlaceholderText(
            """
            请在此区域输入您的问题，点击 Send 或按下 Ctrl+Enter 发送提问
            如果只返回了问题而没有答案，请等待几秒或者换一个模型试试
            """
        )

        self.ui.Button_Load.setText('从文件导入问题')
        self.ui.Button_Load.clicked.connect(self.loadQuestions)

        self.ui.Button_Send.setText('发送')
        self.ui.Button_Send.clicked.connect(self.query)

        self.ui.Button_Stop.setText('停止')
        self.ui.Button_Stop.clicked.connect(self.stopService)

        self.ui.Button_Test.setText('测试')
        self.ui.Button_Test.clicked.connect(self.queryTest)

        # Left area
        self.ui.dockWidget_Left.setFeatures(QDockWidget.DockWidgetMovable)

        self.ui.ListWidget_Conversation.itemClicked.connect(self.loadHistory)
        self.ui.ListWidget_Conversation.setContextMenu(
            actions = {
                "Delete Conversation": self.deleteConversation,
                "Rename Conversation": self.renameConversation,
            }
        )

        self.ui.Button_ClearConversations.setText('清空对话')
        self.ui.Button_ClearConversations.clicked.connect(self.clearConversations)

        self.ui.Button_CreateConversation.setText('创建对话')
        self.ui.Button_CreateConversation.clicked.connect(self.createConversation)

        # Load histories
        self.loadHistories()

        # Set Theme
        ComponentsSignals.Signal_SetTheme.emit(ParamsManager_Chat.config.getValue('Settings', 'Theme', Theme.Auto))

        # Show window
        self.show()

        # Create a new conversation while there is no history conversation
        self.createConversation() if self.ui.ListWidget_Conversation.count() == 0 else self.loadHistory(self.ui.ListWidget_Conversation.item(0))

        # Apply role
        self.applyRole()

        # Set focus to input box
        self.ui.TextEdit_Input.setFocus()

        # Save layout
        QFunc.saveLayout(self, self.settings)

##############################################################################################################################

if __name__ == '__main__':
    App = QApplication(sys.argv)

    SC = QSplashScreen(QPixmap(QFunc.normPath(Path(currentDir).joinpath('assets/images/others/SplashScreen.png'))))
    SC.show()

    window = MainWindow()
    window.main()

    sys.exit(App.exec())

##############################################################################################################################