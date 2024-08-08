# -*- coding: utf-8 -*-

import os
import sys
import argparse
import json
import requests
import pytz
from datetime import date, datetime
from typing import Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtGui import QTextCursor, QAction
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc

from Functions import *
from windows.Windows import *

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
        query = f"model={'gpt-4o' if model is None else model}{f'&testtimes={testtimes}' if testtimes is not None else ''}"
    if type == 'assistant':
        query = f"testtimes={testtimes}" if testtimes is not None else ""
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

    def loadRoles(self):
        # Check if the prompt directory exists
        if not os.path.exists(self.PromptDir):
            os.makedirs(self.PromptDir)
        # Initialize roles and add prompt to combobox
        for HistoryFileName in os.listdir(self.PromptDir):
            if HistoryFileName.endswith('.txt'):
                HistoryFilePath = Path(self.PromptDir).joinpath(HistoryFileName).as_posix()
                if os.path.getsize(HistoryFilePath) == 0:
                    os.remove(HistoryFilePath)
                    continue
                with open(HistoryFilePath, 'r', encoding = 'utf-8') as f:
                    Prompt = f.read()
                self.roles[HistoryFileName[:-4]] = Prompt
        # Update combox
        SelectedRole = self.ui.ComboBox_Role.currentText()
        self.ui.ComboBox_Role.clear()
        self.ui.ComboBox_Role.addItems(list(self.roles.keys()))
        self.ui.ComboBox_Role.setCurrentText(SelectedRole) if SelectedRole in self.roles.keys() else None

    def applyRole(self):
        '''
        if self.ui.ComboBox_Role.count() != len(self.roles.keys()):
            return
        '''
        for ConversationName, Messages in self.MessagesDict.items():
            Messages.append(
                {
                    'role': 'system',
                    'content': self.roles[self.ui.ComboBox_Role.currentText()]
                }
            )
            self.MessagesDict[ConversationName] = Messages

    def manageRole(self):
        ChildWindow_Prompt = PromptWindow(self, self.PromptDir)
        ChildWindow_Prompt.exec()
        # Update roles
        self.roles = {**{"无": ""}, **ChildWindow_Prompt.PromptDict}
        # Update combox
        SelectedRole = self.ui.ComboBox_Role.currentText()
        self.ui.ComboBox_Role.clear()
        self.ui.ComboBox_Role.addItems(list(self.roles.keys()))
        self.ui.ComboBox_Role.setCurrentText(SelectedRole) if SelectedRole in self.roles.keys() else None

    def LoadHistories(self):
        # Check if the conversations directory exists
        if not os.path.exists(self.ConversationDir):
            os.makedirs(self.ConversationDir)
        # Check if the questions directory exists
        if not os.path.exists(self.QuestionDir):
            os.makedirs(self.QuestionDir)
        # Initialize MessagesDict and add conversations&questions to listwidget
        self.ui.ListWidget_Conversation.clear()
        for HistoryFileName in os.listdir(self.ConversationDir):
            if HistoryFileName.endswith('.txt'):
                ConversationFilePath = Path(self.ConversationDir).joinpath(HistoryFileName).as_posix()
                QuestionFilePath = Path(self.QuestionDir).joinpath(HistoryFileName).as_posix()
                if os.path.getsize(ConversationFilePath) == 0:
                    os.remove(ConversationFilePath)
                    os.remove(QuestionFilePath) if Path(QuestionFilePath).exists() else None
                    continue
                with open(ConversationFilePath, 'r', encoding = 'utf-8') as f:
                    Messages = [json.loads(Message) for Message in f.readlines()]
                self.MessagesDict[HistoryFileName[:-4]] = Messages # Remove the .txt extension
                self.ui.ListWidget_Conversation.addItem(HistoryFileName[:-4])

    def loadCurrentHistory(self, item: QStandardItem):
        # Load a conversation from a txt file and display it in the browser
        self.ConversationFilePath = Path(self.ConversationDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.ConversationFilePath, 'r', encoding = 'utf-8') as f:
            Messages = [json.loads(line) for line in f]
        # Build&Set Markdown
        markdown = BuildMessageMarkdown(Messages)
        self.ui.TextBrowser.setMarkdown(markdown)
        # Load a question from the txt file and display it in the input area
        self.QuestionFilePath = Path(self.QuestionDir).joinpath(item.text() + '.txt').as_posix()
        with open(self.QuestionFilePath, 'r', encoding = 'utf-8') as f:
            Question = f.read()
        # Set qustion
        self.ui.TextEdit_Input.setText(Question)

    def removeConversationFiles(self, listItem: QStandardItem):
        self.ui.ListWidget_Conversation.takeItem(self.ui.ListWidget_Conversation.row(listItem))
        os.remove(Path(self.ConversationDir).joinpath(listItem.text() + '.txt').as_posix())
        os.remove(Path(self.QuestionDir).joinpath(listItem.text() + '.txt').as_posix())

    def renameConversation(self):
        currentItem = self.ui.ListWidget_Conversation.currentItem()
        if currentItem is not None:
            old_name = currentItem.text()
            new_name, ok = QInputDialog.getText(self,
                'Rename Conversation',
                'Enter new conversation name:'
            )
            if ok and new_name:
                self.ConversationFilePath = Path(self.ConversationDir).joinpath(f"{new_name}.txt").as_posix()
                os.rename(Path(self.ConversationDir).joinpath(f"{old_name}.txt"), self.ConversationFilePath)
                currentItem.setText(new_name)
                self.QuestionFilePath = Path(self.QuestionDir).joinpath(f"{new_name}.txt").as_posix()
                os.rename(Path(self.QuestionDir).joinpath(f"{old_name}.txt"), self.QuestionFilePath)
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
                    self.loadCurrentHistory(self.ui.ListWidget_Conversation.currentItem()) #self.ui.ListWidget_Conversation.click(self.ui.ListWidget_Conversation.currentItem())
                # Remove message
                self.MessagesDict.pop(old_name)

    def createConversation(self):
        # Get the current time as the name of conversation
        beijing_timezone = pytz.timezone('Asia/Shanghai')
        formatted_time = datetime.now(beijing_timezone).strftime("%Y_%m_%d_%H_%M_%S")
        # Check if the path would be overwritten
        FilePath = Path(self.ConversationDir).joinpath(f"{formatted_time}.txt")
        FilePath = QFunc.RenameFile(FilePath)
        FileName = Path(FilePath).name
        ConversationName = Path(FilePath).stem
        # Update the history file path and the question file path
        self.ConversationFilePath = FilePath
        self.QuestionFilePath = Path(self.QuestionDir).joinpath(FileName).as_posix()
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
        context_menu = QMenu(self)
        delete_action = QAction("Delete Conversation", self)
        delete_action.triggered.connect(self.deleteConversation)
        rename_action = QAction("Rename Conversation", self)
        rename_action.triggered.connect(self.renameConversation)
        context_menu.addActions([delete_action, rename_action])
        context_menu.exec(self.ui.ListWidget_Conversation.mapToGlobal(position))

    def ClearConversations(self):
        listItems = [self.ui.ListWidget_Conversation.item(i) for i in range(self.ui.ListWidget_Conversation.count())]
        for listItem in listItems:
            self.removeConversationFiles(listItem)

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
        if Messages[-1]['role'] == 'user':
            Messages.append({'role': 'assistant', 'content': recievedText})
        '''
        else:
            Messages[-1]['content'] += recievedText
        '''
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
        # 启动参数解析，启动环境，应用端口由命令行传入
        parser = argparse.ArgumentParser()
        parser.add_argument("--promptdir",       help = "prompt目录", type = str)
        parser.add_argument("--conversationdir", help = "对话目录",   type = str)
        parser.add_argument("--questiondir",     help = "问题目录",   type = str)
        parser.add_argument("--configdir",       help = "配置目录",   type = str)
        args = parser.parse_args()

        self.PromptDir = args.promptdir
        self.ConversationDir = args.conversationdir
        self.QuestionDir = args.questiondir
        self.ConfigDir = args.configdir

        # Chat - ParamsManager
        Path_Config_Chat = NormPath(Path(self.ConfigDir).joinpath('Config_Chat.ini'))
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
        self.ui.Button_Maximize_Window.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized())
        self.ui.Button_Minimize_Window.clicked.connect(self.showMinimized)

        # Top area
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
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Type,
            Section = 'Input Params',
            Option = 'Role',
            DefaultValue = "assistant"
        )

        self.ui.Label_Model.setText("模型")
        self.ui.ComboBox_Model.addItems(['gpt-4o', 'dall-e3'])
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Model,
            Section = 'Input Params',
            Option = 'Model',
            DefaultValue = 'gpt-4o'
        )

        self.ui.Label_Role.setText("角色")
        self.ui.ComboBox_Role.addItems(list(self.roles.keys()))
        self.ui.ComboBox_Role.activated.connect(self.applyRole)
        ParamsManager_Chat.SetParam(
            Widget = self.ui.ComboBox_Role,
            Section = 'Input Params',
            Option = 'Role',
            DefaultValue = "无"
        )

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
        self.ui.ListWidget_Conversation.itemClicked.connect(self.loadCurrentHistory)
        self.ui.ListWidget_Conversation.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.ListWidget_Conversation.customContextMenuRequested.connect(self.ShowContextMenu)

        self.ui.Button_ClearConversations.setText('清空对话')
        self.ui.Button_ClearConversations.clicked.connect(self.ClearConversations)

        self.ui.Button_CreateConversation.setText('创建对话')
        self.ui.Button_CreateConversation.clicked.connect(self.createConversation)

        # Load roles
        self.loadRoles()

        # Load histories
        self.LoadHistories()

        # Set Theme
        ComponentsSignals.Signal_SetTheme.emit(ParamsManager_Chat.Config.GetValue('Settings', 'Theme', Theme.Auto))

        # Show window
        self.show()

        # Create a new conversation while there is no history conversation
        self.createConversation() if self.ui.ListWidget_Conversation.count() == 0 else self.loadCurrentHistory(self.ui.ListWidget_Conversation.item(0))

        # Set focus to input box
        self.ui.TextEdit_Input.setFocus()


if __name__ == '__main__':
    App = QApplication(sys.argv)

    window = MainWindow()
    window.Main()

    sys.exit(App.exec())