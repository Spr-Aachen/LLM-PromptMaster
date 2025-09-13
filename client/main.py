# -*- coding: utf-8 -*-

import os
import sys
import argparse
import PyEasyUtils as EasyUtils
from datetime import date, datetime
from pathlib import Path
from typing import Union, Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QSettings
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtGui import QTextCursor, QAction, QStandardItem
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets import componentsSignals, Theme, currentTheme, IconBase, Status
from QEasyWidgets.Windows import InputDialogBase
from QEasyWidgets.Components import MenuBase

from functions import *
from windows import *
from pages import *
from chatExecutor import *

##############################################################################################################################

# Get current path
currentPath = EasyUtils.getCurrentPath()

# Get current directory
currentDir = Path(currentPath).parent.as_posix()

# Check whether python file is compiled
_, isFileCompiled = EasyUtils.getFileInfo()

##############################################################################################################################

# 启动参数解析，启动环境，应用端口由命令行传入
parser = argparse.ArgumentParser()
parser.add_argument("--host", help = "主机地址",   type = str, default = "localhost")
parser.add_argument("--port", help = "端口",       type = int, default = 8080)
parser.add_argument("--profileDir", help = "配置目录", type = str, default = Path(currentDir).joinpath('Profile').as_posix())
args = parser.parse_args()

profileDir = args.profileDir
configDir = Path(profileDir).joinpath('config').as_posix()

##############################################################################################################################

class LoadWindow(Window_LoadWindow):
    def __init__(self):
        super().__init__()

    def loadQuestions(self):
        filePath = self.lineEdit_filePath.text()
        if Path(filePath).exists():
            excelDF = pandas.read_excel(filePath, usecols = self.lineEdit_column.text().strip())
            self.questionList = excelDF.iloc[:, 0].to_list()
        maximumAmount = self.lineEdit_amount.text().strip()
        if maximumAmount.__len__() > 0 and self.questionList.__len__() > int(maximumAmount) > 0 :
            self.questionList = self.questionList[:int(maximumAmount)]

    def initUI(self):
        self.label.setText("Plz provide ur excel file path and its column letter:")

        self.lineEdit_filePath.setFileDialog('SelectFile', '表格 (*.csv *.xlsx)')
        self.lineEdit_filePath.setAcceptDrops(True)
        self.lineEdit_filePath.setPlaceholderText("Please enter the excel file path to load")

        self.lineEdit_column.setAcceptDrops(False)
        self.lineEdit_column.setPlaceholderText("Please enter the column where questions are located")

        self.lineEdit_amount.setAcceptDrops(False)
        self.lineEdit_amount.setPlaceholderText("Please enter the maximum amount of questions")

        self.button_confirm.clicked.connect(self.loadQuestions, Qt.ConnectionType.QueuedConnection)
        self.button_confirm.clicked.connect(self.close, Qt.ConnectionType.QueuedConnection)

        self.button_cancel.clicked.connect(self.close)


class PromptWindow(Window_PromptWindow):
    def __init__(self):
        super().__init__()

    def showContextMenu(self, position):
        context_menu = QMenu(self)
        delete_action = QAction("Delete Prompt", self)
        delete_action.triggered.connect(self.deleteCurrentPrompt)
        rename_action = QAction("Rename Prompt", self)
        rename_action.triggered.connect(self.renameCurrentPrompt)
        context_menu.addActions([delete_action, rename_action])
        context_menu.exec(self.listWidget.mapToGlobal(position))

    def _setPromptID(self, item: QStandardItem, promptID):
        item.setWhatsThis(promptID)

    def _getPromptID(self, item: QStandardItem):
        return item.whatsThis() if item else None

    def roles(self):
        return [item.text() for item in [self.listWidget.item(row) for row in range(self.listWidget.count())]]

    def currentRoleItem(self):
        return self.listWidget.currentItem()

    def currentPromptID(self):
        return self._getPromptID(self.currentRoleItem())

    def currentRole(self):
        return self.currentRoleItem().text() if self.currentRoleItem() else None

    def loadPrompts(self):
        # Initialize roles and add prompt to listwidget
        self.listWidget.clear()
        for promptID, promptName in EasyUtils.simpleRequest(EasyUtils.requestManager.Get, "http", args.host, args.port, 'chat/loadPrompts', None).items():
            item = QStandardItem()
            self._setPromptID(item, promptID)
            item.setText(promptName)
            self.listWidget.addItem(item)

    def loadPrompt(self, item: QStandardItem):
        # Load prompt
        promptID = self._getPromptID(item)
        prompt = EasyUtils.simpleRequest(EasyUtils.requestManager.Get, "http", args.host, args.port, 'chat/getPrompt', f'promptID={promptID}')
        # Set prompt
        self.textEdit.setText(prompt)

    def createPrompt(self, name: Optional[str] = None):
        # Get the current time as the name of prompt
        promptName = datetime.now().strftime("%Y%m%d%H%M%S") if name is None else name
        # 
        promptID, promptName = EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/createPrompt', f'name={EasyUtils.makeSafeForURL(promptName)}')
        # Set role item
        item = QStandardItem(promptName)
        self._setPromptID(item, promptID)
        # Add to the prompt list and load it
        self.listWidget.addItem(item)
        self.listWidget.setCurrentItem(item)# if self.currentRoleItem() != item else None
        self.loadPrompt(item)
        # Set focus to input box
        self.textEdit.setFocus()

    def renameCurrentPrompt(self):
        item = self.currentRoleItem()
        if item is not None:
            newName, ok = InputDialogBase.getText(self,
                'Rename Prompt',
                'Enter new prompt name:'
            )
            if ok and newName:
                promptID = self._getPromptID(item)
                EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/renamePrompt', f'promptID={promptID}&newName={EasyUtils.makeSafeForURL(newName)}')
                item.setText(newName)

    def deleteCurrentPrompt(self):
        item = self.currentRoleItem()
        if item is not None:
            confirm = MessageBoxBase.pop(self,
                QMessageBox.Question, 'Delete Prompt',
                text = 'Are you sure you want to delete this Prompt?',
                buttons = QMessageBox.Yes | QMessageBox.No,
            )
            if confirm == QMessageBox.Yes:
                promptID = self._getPromptID(item)
                EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/deletePrompt', f'promptID={promptID}')
                self.listWidget.takeItem(self.listWidget.row(item))
                # 
                if self.roles().__len__() > 0:
                    self.listWidget.click(self.currentRoleItem())
                else:
                    self.textEdit.clear()

    def savePrompt(self, prompt: str):
        promptID = self._getPromptID(self.currentRoleItem())
        if promptID is None:
            return
        EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/savePrompt', f'promptID={promptID}&prompt={EasyUtils.makeSafeForURL(prompt)}')

    def initUI(self):
        self.titleArea.setText('Prompt Manager')

        self.textEdit.textChanged.connect(lambda: self.savePrompt(self.textEdit.toPlainText()))
        self.textEdit.setPlaceholderText(
            """
            请在此区域输入Prompt
            """
        )

        self.button_createPrompt.setText('Create Prompt')
        self.button_createPrompt.clicked.connect(lambda: self.createPrompt(None))

        self.button_deletePrompt.setText('Delete Prompt')
        self.button_deletePrompt.clicked.connect(self.deleteCurrentPrompt)

        self.listWidget.itemClicked.connect(lambda item: self.loadPrompt(item))
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.showContextMenu)


class MainWindow(Window_MainWindow):
    chatRequestWorker = None

    chatRoleDict = {
        'user': ChatRole.User,
        'assistant': ChatRole.Contact,
        'system': None
    }

    def __init__(self):
        super().__init__()

        #self.settings = QSettings(self)

        self.threadPool = QThreadPool()

        self.promptWindow = PromptWindow()
        self.promptWindow.initUI()

    def closeEvent(self, event):
        self.exitService()
        QApplication.instance().exit()

    def _setHistoryID(self, item: QStandardItem, historyID):
        item.setWhatsThis(historyID)

    def _getHistoryID(self, item: QStandardItem):
        return item.whatsThis() if item else None

    def conversationNames(self):
        return [item.text() for item in [self.subChatPage.listWidget_history.item(row) for row in range(self.subChatPage.listWidget_history.count())]]

    def currentConversationItem(self):
        return self.subChatPage.listWidget_history.currentItem()

    def currentHistoryID(self):
        return self._getHistoryID(self.currentConversationItem())

    def currentConversationName(self):
        return self.currentConversationItem().text()

    def manageRole(self):
        # Show prompt window
        self.promptWindow.exec()
        # Update roles
        self.roles = self.promptWindow.roles()
        # Apply current role
        currentRole = self.promptWindow.currentRole()
        if currentRole is not None:
            # Update role display
            self.subChatPage.display_role.setText(currentRole)

    def loadHistories(self):
        # Initialize messagesDict and add conversations&questions to listwidget
        self.subChatPage.listWidget_history.clear()
        for historyID, conversationName in EasyUtils.simpleRequest(EasyUtils.requestManager.Get, "http", args.host, args.port, 'chat/loadHistories', None).items():
            item = QStandardItem()
            self._setHistoryID(item, historyID)
            item.setText(conversationName)
            self.subChatPage.listWidget_history.addItem(item)

    def _setMessages(self, messages: list[dict]):
        cleanedMessages = []
        for message in messages:
            cleanedMessage = {}
            role = str(message['role']).strip()
            content = str(message['content']).strip()
            if len(content) == 0:
                continue
            content = EasyUtils.toMarkdown(content)
            cleanedMessage[role] = content
            cleanedMessages.append(cleanedMessage)
        self.subChatPage.messageBrowser.clear()
        for message in cleanedMessages:
            chatRole = self.chatRoleDict[list(message.keys())[0]]
            self.subChatPage.messageBrowser.addMessage(
                list(message.values())[0], chatRole, None
            ) if chatRole else None

    def loadHistory(self, item: QStandardItem):
        # Load conversation and question
        historyID = self._getHistoryID(item)
        messages, question = EasyUtils.simpleRequest(EasyUtils.requestManager.Get, "http", args.host, args.port, 'chat/getHistory', f'historyID={historyID}')
        # Set messages
        self._setMessages(messages)
        # Set qustion
        self.subChatPage.inputEdit.setText(question)

    def createConversation(self, name: Optional[str] = None):
        # Get the current time as the name of conversation
        conversationName = datetime.now().strftime("%Y%m%d%H%M%S") if name is None else name
        # 
        historyID, conversationName = EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/createConversation', f'name={EasyUtils.makeSafeForURL(conversationName)}')
        # Set conversation item
        item = QStandardItem(conversationName)
        self._setHistoryID(item, historyID)
        # Add to the history list and select it
        self.subChatPage.listWidget_history.addItem(item)
        self.subChatPage.listWidget_history.setCurrentItem(item)# if self.currentConversationItem() != item else None
        self.loadHistory(item)
        # Set focus to input box
        self.subChatPage.inputEdit.setFocus()

    def renameConversation(self):
        item = self.currentConversationItem()
        if item is not None:
            newName, ok = InputDialogBase.getText(self,
                'Rename Conversation',
                'Enter new conversation name:'
            )
            if ok and newName:
                historyID = self._getHistoryID(item)
                EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/renameConversation', f'historyID={historyID}&newName={EasyUtils.makeSafeForURL(newName)}')
                item.setText(newName)

    def deleteConversation(self):
        item = self.currentConversationItem()
        if item is not None:
            confirm = MessageBoxBase.pop(self,
                QMessageBox.Question, 'Delete Conversation',
                text = 'Sure you wanna delete this conversation?',
                buttons = QMessageBox.Yes | QMessageBox.No,
            )
            if confirm == QMessageBox.Yes:
                historyID = self._getHistoryID(item)
                EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/deleteConversation', f'historyID={historyID}')
                self.subChatPage.listWidget_history.takeItem(self.subChatPage.listWidget_history.row(item))
                # 
                if self.conversationNames().__len__() > 0:
                    self.subChatPage.listWidget_history.click(self.currentConversationItem())
                else:
                    self.subChatPage.messageBrowser.clear()

    def saveQuestion(self, historyID, question: str):
        if self.currentConversationItem() is None:
            return
        EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/saveQuestion', f'historyID={historyID}&question={EasyUtils.makeSafeForURL(question)}')

    def applyPrompt(self):
        promptID = self.promptWindow.currentPromptID()
        if promptID is None:
            return
        EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/applyPrompt', f'promptID={promptID}')

    def _addMessage(self, currentRole: str, messages: Union[dict, list[dict], None], status: Status = None):
        if status is not None:
            self.subChatPage.messageBrowser.addMessage(
                '', ChatRole.Contact, status, False
            )
            return
        for message in reversed(messages if isinstance(messages, list) else [messages]):
            if message is None:
                continue
            role = str(message['role']).strip()
            content = str(message['content']).strip()
            if role != currentRole or len(content) == 0:
                continue
            self.subChatPage.messageBrowser.addMessage(
                EasyUtils.toMarkdown(content),
                role = self.chatRoleDict[currentRole],
                status = status,
                stream = True if currentRole == 'assistant' else False,
            )
            break

    def recieveAnswer(self, historyID, recievedText, conversationName):
        messages = EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/recieveAnswer', f'historyID={historyID}&recievedText={recievedText}')
        # Update assistant message
        self._addMessage('assistant', messages) if self.currentConversationName() == conversationName else None

    def sendMessage(self):
        totalTestTimes = None
        if self.subChatPage.checkbox_testMode.isChecked():
            totalTestTimes, ok = InputDialogBase.getText(self,
                'Set Testing Times',
                'Enter testing times:'
            )
            if ok and totalTestTimes.strip().__len__() > 0:
                totalTestTimes = int(totalTestTimes.strip())
                if totalTestTimes <= 0:
                    MessageBoxBase.pop(self,
                        QMessageBox.Warning, 'Warning',
                        'Incorrect number!'
                    )
        inputContent = self.subChatPage.inputEdit.toPlainText()
        if inputContent.strip().__len__() == 0:
            return
        # Block input
        self.subChatPage.blockInput(True)
        # Create conversation
        self.createConversation() if self.currentConversationItem() is None else None
        # Apply role
        self.applyPrompt()
        # Get historyID and conversationName
        historyID = self.currentHistoryID()
        conversationName = self.currentConversationName()
        # Set new user message
        newMessage = {'role': 'user', 'content': inputContent}
        # Display new user message
        self._addMessage('user', newMessage)
        # Update user messages
        EasyUtils.simpleRequest(EasyUtils.requestManager.Post, "http", args.host, args.port, 'chat/addUserMessage', f'historyID={historyID}&userMessage={EasyUtils.makeSafeForURL(newMessage)}')
        # Start a new thread to send the request
        chatRequestTask = task_chatRequest()
        self.chatRequestWorker = WorkerManager(
            executeMethod = chatRequestTask.execute,
            executeParams = (
                args.host, args.port,
                historyID,
                self.subChatPage.comboBox_source.currentText(),
                None, #self.subChatPage.comboBox_env.currentText(),
                self.subChatPage.comboBox_type.currentText(),
                self.subChatPage.comboBox_model.currentText(),
                self.subChatPage.lineEdit_assistantID.text(),
                newMessage,
                None,
                self.subSettingsPage.apiKeyTable.getValue().get(self.subChatPage.comboBox_source.currentText(), None),
                totalTestTimes
            ),
            terminateMethod = chatRequestTask.terminate,
            threadPool = self.threadPool
        )
        self.chatRequestWorker.signals.result.connect(
            lambda text: (
                self.recieveAnswer(historyID, text, conversationName),
                self.subChatPage.blockInput(False)
            )
        )
        self.chatRequestWorker.execute()
        self._addMessage('assistant', None, Status.Loading)
        self.subChatPage.inputEdit.clear()
        self.subChatPage.inputEdit.setFocus()

    def exitService(self):
        exitService()

    def stopService(self):
        if self.chatRequestWorker is not None:
            self.chatRequestWorker.terminate()

    def main(self):
        # ParamsManager
        configPath = EasyUtils.normPath(Path(configDir).joinpath('config.ini'))
        paramsManager = ParamsManager(configPath)

        # Logo
        self.setWindowIcon(QIcon(EasyUtils.normPath(Path(currentDir).joinpath('assets/images/Logo.ico'))))

        # Theme toggler
        componentsSignals.setTheme.connect(
            lambda: self.ui.CheckBox_SwitchTheme.setChecked(
                {Theme.Light: True, Theme.Dark: False}.get(currentTheme())
            )
        )
        Function_ConfigureCheckBox(
            checkBox = self.ui.CheckBox_SwitchTheme,
            checkedText = "☀",
            checkedEvents = {
                lambda: paramsManager.config.editConfig('Settings', 'Theme', Theme.Light): False,
                lambda: componentsSignals.setTheme.emit(Theme.Light) if currentTheme() != Theme.Light else None : False
            },
            uncheckedText = "☼",
            uncheckedEvents = {
                lambda: paramsManager.config.editConfig('Settings', 'Theme', Theme.Dark) : False,
                lambda: componentsSignals.setTheme.emit(Theme.Dark) if currentTheme() != Theme.Dark else None : False
            }
        )

        # Window controling buttons
        self.ui.Button_Close_Window.clicked.connect(self.close)
        self.ui.Button_Close_Window.setBorderless(True)
        self.ui.Button_Close_Window.setTransparent(True)
        self.ui.Button_Close_Window.setHoverBackgroundColor(QColor(210, 123, 123, 210))
        self.ui.Button_Close_Window.setIcon(IconBase.X)

        self.ui.Button_Maximize_Window.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized())
        self.ui.Button_Maximize_Window.setBorderless(True)
        self.ui.Button_Maximize_Window.setTransparent(True)
        self.ui.Button_Maximize_Window.setHoverBackgroundColor(QColor(123, 123, 123, 123))
        self.ui.Button_Maximize_Window.setIcon(IconBase.FullScreen)

        self.ui.Button_Minimize_Window.clicked.connect(self.showMinimized)
        self.ui.Button_Minimize_Window.setBorderless(True)
        self.ui.Button_Minimize_Window.setTransparent(True)
        self.ui.Button_Minimize_Window.setHoverBackgroundColor(QColor(123, 123, 123, 123))
        self.ui.Button_Minimize_Window.setIcon(IconBase.Dash)

        # # Actions
        # action_ResetLayout = QAction(QCA.translate("Action", "重置布局"), self)
        # action_ResetLayout.triggered.connect(lambda: QFunc.resetLayout(self, self.settings))

        # # MenuBar
        # menuButton_Layout = QMenu(QCA.translate("Menu", "布局"))
        # menuButton_Layout.addAction(action_ResetLayout)

        # menuButton_Help = QMenu(QCA.translate("Menu", "帮助"))

        # menuBar = QMenuBar()
        # menuBar.addMenu(menuButton_Layout)
        # menuBar.addSeparator()
        # menuBar.addMenu(menuButton_Help)
        # menuBar.addSeparator()
        # menuBar.setFixedWidth(menuButton_Layout.sizeHint().width() + menuButton_Help.sizeHint().width())
        # self.setMenuBar(menuBar)

        # Menu toggling button
        self.ui.Button_Toggle_Menu.clicked.connect(
            lambda: Function_AnimateFrame(
                frame = self.ui.Frame_Menu,
                minWidth = 48,
                maxWidth = 123
            )
        )
        self.ui.Button_Toggle_Menu.setChecked(False)
        self.ui.Button_Toggle_Menu.setToolTip(QCA.translate('MainWindow', "点击以展开/折叠菜单"))

        #############################################################
        ############################ Menu ###########################
        #############################################################

        self.ui.Button_Menu_Home.setText(QCA.translate('MainWindow', "主页"))
        self.ui.Button_Menu_Home.clicked.connect(
            lambda: Function_AnimateStackedWidget(
                stackedWidget = self.ui.StackedWidget_Pages,
                target = 0
            )
        )
        self.ui.Button_Menu_Home.setChecked(True)
        self.ui.Button_Menu_Home.setToolTip(QCA.translate('MainWindow', "主页"))

        self.ui.Button_Menu_Env.setText(QCA.translate('MainWindow', "聊天"))
        self.ui.Button_Menu_Env.clicked.connect(
            lambda: Function_AnimateStackedWidget(
                stackedWidget = self.ui.StackedWidget_Pages,
                target = 1
            )
        )
        self.ui.Button_Menu_Env.setChecked(False)
        self.ui.Button_Menu_Env.setToolTip(QCA.translate('MainWindow', "LLM聊天"))

        self.ui.Button_Menu_Settings.setText(QCA.translate('MainWindow', "设置"))
        self.ui.Button_Menu_Settings.clicked.connect(
            lambda: Function_AnimateStackedWidget(
                stackedWidget = self.ui.StackedWidget_Pages,
                target = 2
            )
        )
        self.ui.Button_Menu_Settings.setChecked(False)
        self.ui.Button_Menu_Settings.setToolTip(QCA.translate('MainWindow', "客户端设置"))

        # HomePage
        self.ui.Label_HomePage.setText("LLM PromptMaster\nVersion 1.0.0")

        # Chat - ParamsManager
        configPath_chat = EasyUtils.normPath(Path(configDir).joinpath('config_chat.ini'))
        paramsManager_chat = ParamsManager(configPath_chat)

        # view
        self.subChatPage = SubChatPage(self.ui.Page_Chat, paramsManager_chat)
        self.subChatPage.setModelSettingFrame(
            rootItemText = QCA.translate("MainWindow", "设置"),
            text = "来源与模型",
            modelInfos = EasyUtils.simpleRequest(EasyUtils.requestManager.Get, "http", args.host, args.port, 'chat/getModelsInfo', None),
            modelSection = 'Input Params',
            modelOption = 'Model',
            modelDefaultValue = None,
            sourceSection = 'Input Params',
            sourceOption = 'Source',
            sourceDefaultValue = None
        )
        self.subChatPage.setRoleSettingFrame(
            rootItemText = QCA.translate("MainWindow", "设置"),
            text = "类型与角色",
            manageRoleEvent = self.manageRole,
            assistantIDSection = 'Input Params',
            assistantIDOption = 'AssistantID',
            assistantIDDefaultValue = None,
            placeholderText = "Please enter the assistant's ID",
            typeSection = 'Input Params',
            typeOption = 'Type',
            typeDefaultValue = "gpt"
        )
        self.subChatPage.setChatFrame(
            text = "聊天区域",
            listItemClickedEvent = lambda item: self.loadHistory(item),
            contextMenuActions = {
                "Delete Conversation": self.deleteConversation,
                "Rename Conversation": self.renameConversation,
            },
            createConversationEvent = lambda: self.createConversation(None),
            inputEditTextChangedEvent = lambda: self.saveQuestion(
                self.currentHistoryID(),
                self.subChatPage.inputEdit.toPlainText()
            ) if self.currentConversationItem() is not None else None,
            inputEditKeyEnterPressedEvent = self.sendMessage,
            inputEditPlaceholderText = """
            请在此区域输入您的问题，点击 Send 或按下 Ctrl+Enter 发送提问
            如果只返回了问题而没有答案，请等待几秒或者换一个模型试试
            """,
            #loadQuestionsEvent = self.loadQuestions,
            sendEvent = self.sendMessage,
            stopEvent = lambda: (
                self.stopService,
                Function_AnimateStackedWidget(
                    self.subChatPage.stackedWidget_sendAndStop,
                    self.subChatPage.stackedWidgetPage_send
                )
            ),
        )

        self.ui.Page_Chat.addSubPage(
            QCA.translate('MainWindow', "对话页面"), self.subChatPage, showNavigator = False
        )

        self.subSettingsPage = SubSettingsPage(self.ui.Page_Settings, paramsManager)
        self.subSettingsPage.setAPIKeyTableFrame(
            rootItemText = QCA.translate('MainWindow', "参数设置"),
            text = QCA.translate('MainWindow', "API Key"),
            headerLabels = ["源", "API Key"],
            section = 'Chat Params',
            option = 'API Keys',
            defaultValue = {source: '' for source in EasyUtils.simpleRequest(EasyUtils.requestManager.Get, "http", args.host, args.port, 'chat/getModelsInfo', None).keys()}
        )

        self.ui.Page_Settings.addSubPage(
            QCA.translate('MainWindow', "设置页面"), self.subSettingsPage, showNavigator = True
        )

        # Load prompts
        self.promptWindow.loadPrompts()

        # Load histories
        self.loadHistories()
        # Create a new conversation while there is no history conversation
        self.createConversation() if self.conversationNames().__len__() == 0 else None

        # Set focus to input box
        self.subChatPage.inputEdit.setFocus()

        # Set Theme
        componentsSignals.setTheme.emit(paramsManager_chat.config.getValue('Settings', 'Theme', Theme.Auto))

        # Show window
        self.show()

        # # Save layout
        # QFunc.saveLayout(self, self.settings)

##############################################################################################################################

if __name__ == '__main__':
    App = QApplication(sys.argv)

    SC = QSplashScreen(QPixmap(EasyUtils.normPath(Path(currentDir).joinpath('assets/images/others/SplashScreen.png'))))
    SC.show()

    window = MainWindow()
    window.main()

    sys.exit(App.exec())

##############################################################################################################################