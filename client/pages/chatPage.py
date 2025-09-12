from typing import Type, Optional
from PyEasyUtils import setRichText
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets import IconBase, Status
from QEasyWidgets.Common import FileDialogMode
from QEasyWidgets.Components import *
from QEasyWidgets import QTasks

from .common import SubPage, Page
#from assets import *
from functions import *

##############################################################################################################################

class SubChatPage(SubPage):
    """
    """
    def __init__(self, parent = None, paramsManager: ParamsManager = ...):
        super().__init__(parent)

        self.paramsManager = paramsManager

        layout = self.cleanLayout()
        layout.addWidget(self.contentWidget, 0, 0)

    def _addRoleSettingFrame(self,
        rootItemText: Optional[str] = None, toolBoxText: Optional[str] = None, text: str = ...,
    ):
        # Role&AssistantID
        self.stackedWidget_roleOrAssistant = QStackedWidget()
        # role
        page1 = QWidget()
        label_role = LabelBase()
        label_role.setText("角色")
        self.display_role = LabelBase()
        self.display_role.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self.button_manageRole = HollowButton()
        self.button_manageRole.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self.button_manageRole.setIcon(IconBase.Ellipsis)
        self.button_manageRole.setToolTip("管理角色")
        self.checkbox_testMode = CheckBoxBase()
        self.checkbox_testMode.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self.checkbox_testMode.setText('测试模式')
        layout_role = QHBoxLayout()
        layout_role.setSpacing(12)
        layout_role.addWidget(label_role)
        layout_role.addWidget(self.display_role)
        layout_role.addWidget(self.button_manageRole)
        layout_role.addWidget(self.checkbox_testMode)
        page1Layout = QHBoxLayout(page1)
        page1Layout.setSpacing(21)
        page1Layout.setContentsMargins(0, 0, 0, 0)
        page1Layout.addLayout(layout_role)
        # assistantID
        page2 = QWidget()
        layout_assistantID = QHBoxLayout()
        layout_assistantID.setSpacing(12)
        label_assistantID = LabelBase()
        label_assistantID.setText("助手ID")
        label_assistantID.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed))
        layout_assistantID.addWidget(label_assistantID)
        self.lineEdit_assistantID = LineEditBase()
        layout_assistantID.addWidget(self.lineEdit_assistantID)
        page2Layout = QHBoxLayout(page2)
        page2Layout.setSpacing(21)
        page2Layout.setContentsMargins(0, 0, 0, 0)
        page2Layout.addLayout(layout_assistantID)
        # merge
        self.stackedWidget_roleOrAssistant.addWidget(page1)
        self.stackedWidget_roleOrAssistant.addWidget(page2)

        # Type
        layout_type = QHBoxLayout()
        layout_type.setSpacing(12)
        label_type = LabelBase()
        label_type.setText("类型")
        layout_type.addWidget(label_type)
        self.comboBox_type = ComboBoxBase()
        self.comboBox_type.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        layout_type.addWidget(self.comboBox_type)

        # Merge
        layout = QGridLayout()
        layout.addLayout(layout_type, 0, 0)
        layout.addWidget(self.stackedWidget_roleOrAssistant, 0, 1)

        self._addToContainer(rootItemText, toolBoxText, text, layout, QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))

    def setRoleSettingFrame(self,
        rootItemText: Optional[str] = None, toolBoxText: Optional[str] = None, text: str = ...,
        manageRoleEvent: object = ...,
        assistantIDSection: str = ..., assistantIDOption: str = ..., assistantIDDefaultValue: str = ..., placeholderText: str = "",
        typeSection: str = ..., typeOption: str = ..., typeDefaultValue: str = ...,
    ):
        self._addRoleSettingFrame(rootItemText, toolBoxText, text)
        # role
        self.button_manageRole.clicked.connect(manageRoleEvent)
        # assistantID
        self.paramsManager.setParam(self.lineEdit_assistantID, assistantIDSection, assistantIDOption, assistantIDDefaultValue, True, placeholderText)
        # type
        self.comboBox_type.addItems(['gpt', 'assistant'])
        self.comboBox_type.currentTextChanged.connect(
            lambda text: (
                self.stackedWidget_roleOrAssistant.setCurrentIndex(0 if text == 'gpt' else 1),
            )
        )
        self.paramsManager.setParam(self.comboBox_type, typeSection, typeOption, typeDefaultValue)

    def _addModelSettingFrame(self,
        rootItemText: Optional[str] = None, toolBoxText: Optional[str] = None, text: str = ...,
    ):
        # Model
        layout_model = QHBoxLayout()
        layout_model.setSpacing(12)
        label_model = LabelBase()
        label_model.setText("模型")
        layout_model.addWidget(label_model)
        self.comboBox_model = ComboBoxBase()
        self.comboBox_model.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        layout_model.addWidget(self.comboBox_model)

        # Source
        layout_source = QHBoxLayout()
        layout_source.setSpacing(12)
        label_source = LabelBase()
        label_source.setText("来源")
        layout_source.addWidget(label_source)
        self.comboBox_source = ComboBoxBase()
        self.comboBox_source.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        layout_source.addWidget(self.comboBox_source)

        # Merge
        layout = QGridLayout()
        layout.addLayout(layout_source, 0, 0)
        layout.addLayout(layout_model, 0, 1)

        self._addToContainer(rootItemText, toolBoxText, text, layout, QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))

    def setModelSettingFrame(self,
        rootItemText: Optional[str] = None, toolBoxText: Optional[str] = None, text: str = ...,
        modelInfos: dict = ...,
        modelSection: str = ..., modelOption: str = ..., modelDefaultValue: str = ...,
        sourceSection: str = ..., sourceOption: str = ..., sourceDefaultValue: str = ...,
    ):
        self._addModelSettingFrame(rootItemText, toolBoxText, text)

        self.comboBox_source.currentTextChanged.connect(
            lambda text: (
                self.comboBox_model.clear(),
                self.comboBox_model.addItems(list(modelInfos[text]))
            )
        )
        self.comboBox_source.addItems(list(modelInfos.keys()))
        self.paramsManager.setParam(self.comboBox_source, sourceSection, sourceOption, sourceDefaultValue)

        self.paramsManager.setParam(self.comboBox_model, modelSection, modelOption, modelDefaultValue)

    def _addChatFrame(self,
        rootItemText: Optional[str] = None, toolBoxText: Optional[str] = None, text: str = ...,
    ):
        # List
        self.listWidget_history = ListBase()
        self.button_createConversation = HollowButton()
        self.button_createConversation.setText('创建对话')
        # 
        listLayout = QGridLayout()
        listLayout.setSpacing(12)
        listLayout.setContentsMargins(12, 0, 12, 12)
        listLayout.addWidget(self.listWidget_history, 0, 0, 1, 1)
        listLayout.addWidget(self.button_createConversation, 1, 0, 1, 1)

        # Browser
        self.messageBrowser = ChatWidgetBase()
        self.messageBrowser.setMinimumSize(QSize(0, 123))
        self.inputEdit = TextEditBase()
        splitter = QSplitter()
        splitter.setStyleSheet("""
            QSplitter {
                background: transparent;
                border: none;
            }
            QSplitter::handle {
                background: transparent;
                border: none;
            }
        """)
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.setHandleWidth(6)
        splitter.addWidget(self.messageBrowser)
        splitter.addWidget(self.inputEdit)
        splitter.setStretchFactor(0, 1)
        # 
        self.button_send = HollowButton()
        self.button_send.setText('发送')
        self.button_stop = HollowButton()
        self.button_stop.setText('停止')
        self.stackedWidgetPage_send = QWidget()
        stackedWidgetPage_send_layout = QGridLayout(self.stackedWidgetPage_send)
        stackedWidgetPage_send_layout.setHorizontalSpacing(12)
        stackedWidgetPage_send_layout.setVerticalSpacing(0)
        stackedWidgetPage_send_layout.setContentsMargins(0, 0, 0, 0)
        stackedWidgetPage_send_layout.addWidget(self.button_send, 0, 0, 1, 1)
        stackedWidgetPage_send_layout.addWidget(self.button_send, 0, 1, 1, 1)
        self.stackedWidgetPage_stop = QWidget()
        stackedWidgetPage_stop_layout = QGridLayout(self.stackedWidgetPage_stop)
        stackedWidgetPage_stop_layout.setSpacing(0)
        stackedWidgetPage_stop_layout.setContentsMargins(0, 0, 0, 0)
        stackedWidgetPage_stop_layout.addWidget(self.button_stop, 0, 0, 1, 1)
        self.stackedWidget_sendAndStop = QStackedWidget()
        self.stackedWidget_sendAndStop.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed))
        self.stackedWidget_sendAndStop.addWidget(self.stackedWidgetPage_send)
        self.stackedWidget_sendAndStop.addWidget(self.stackedWidgetPage_stop)
        # 
        browserLayout = QGridLayout()
        browserLayout.setSpacing(12)
        browserLayout.setContentsMargins(12, 0, 12, 12)
        browserLayout.addWidget(splitter, 0, 0, 1, 1)
        browserLayout.addWidget(self.stackedWidget_sendAndStop, 1, 0, 1, 1)

        # Merge
        layout = QHBoxLayout()
        layout.addLayout(listLayout, 0)
        layout.addLayout(browserLayout, 1)

        self._addToContainer(rootItemText, toolBoxText, text, layout, QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

    def setChatFrame(self,
        rootItemText: Optional[str] = None, toolBoxText: Optional[str] = None, text: str = ...,
        listItemClickedEvent: object = ..., contextMenuActions: dict = ..., createConversationEvent: object = ...,
        inputEditTextChangedEvent: object = ..., inputEditKeyEnterPressedEvent: object = ... , inputEditPlaceholderText: str = ...,
        sendEvent: object = ..., stopEvent: object = ...,
    ):
        self._addChatFrame(rootItemText, toolBoxText, text)

        self.listWidget_history.itemClicked.connect(listItemClickedEvent)
        self.listWidget_history.setContextMenu(contextMenuActions)
        self.button_createConversation.clicked.connect(createConversationEvent)

        self.inputEdit.textChanged.connect(inputEditTextChangedEvent)
        self.inputEdit.keyEnterPressed.connect(inputEditKeyEnterPressedEvent)
        self.inputEdit.setPlaceholderText(inputEditPlaceholderText)
        self.button_send.clicked.connect(sendEvent)
        self.button_stop.clicked.connect(stopEvent)

    def blockInput(self, block: bool):
        self.comboBox_type.setDisabled(block)
        self.comboBox_source.setDisabled(block)
        self.comboBox_model.setDisabled(block)
        self.button_manageRole.setDisabled(block)
        self.listWidget_history.setDisabled(block)
        self.button_createConversation.setDisabled(block)
        self.button_send.setDisabled(block)
        self.inputEdit.blockKeyEnter(block)


class ChatPage(Page):
    """
    """
    def __init__(self, parent = None):
        super().__init__(parent)

##############################################################################################################################