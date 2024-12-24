# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import *

from components import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.dockWidget_Top = DockWidgetBase(MainWindow)
        self.dockWidget_Top.setObjectName(u"dockWidget_Top")
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.gridLayout_3 = QGridLayout(self.dockWidgetContents_3)
        self.gridLayout_3.setSpacing(12)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(12, 0, 12, 12)
        self.groupBox_Settings = GroupBoxBase(self.dockWidgetContents_3)
        self.groupBox_Settings.setObjectName(u"groupBox_Settings")
        self.gridLayout_34 = QGridLayout(self.groupBox_Settings)
        self.gridLayout_34.setObjectName(u"gridLayout_34")
        self.gridLayout_34.setHorizontalSpacing(21)
        self.gridLayout_34.setVerticalSpacing(12)
        self.gridLayout_34.setContentsMargins(0, 12, 0, 0)
        self.Layout_Type = QHBoxLayout()
        self.Layout_Type.setSpacing(12)
        self.Layout_Type.setObjectName(u"Layout_Type")
        self.Label_Type = LabelBase(self.groupBox_Settings)
        self.Label_Type.setObjectName(u"Label_Type")

        self.Layout_Type.addWidget(self.Label_Type)

        self.ComboBox_Type = ComboBoxBase(self.groupBox_Settings)
        self.ComboBox_Type.setObjectName(u"ComboBox_Type")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ComboBox_Type.sizePolicy().hasHeightForWidth())
        self.ComboBox_Type.setSizePolicy(sizePolicy)

        self.Layout_Type.addWidget(self.ComboBox_Type)


        self.gridLayout_34.addLayout(self.Layout_Type, 0, 0, 1, 1)

        self.Layout_Model = QHBoxLayout()
        self.Layout_Model.setSpacing(12)
        self.Layout_Model.setObjectName(u"Layout_Model")
        self.Label_Model = LabelBase(self.groupBox_Settings)
        self.Label_Model.setObjectName(u"Label_Model")

        self.Layout_Model.addWidget(self.Label_Model)

        self.ComboBox_Model = ComboBoxBase(self.groupBox_Settings)
        self.ComboBox_Model.setObjectName(u"ComboBox_Model")
        sizePolicy.setHeightForWidth(self.ComboBox_Model.sizePolicy().hasHeightForWidth())
        self.ComboBox_Model.setSizePolicy(sizePolicy)

        self.Layout_Model.addWidget(self.ComboBox_Model)


        self.gridLayout_34.addLayout(self.Layout_Model, 0, 1, 1, 1)

        self.Layout_Source = QHBoxLayout()
        self.Layout_Source.setSpacing(12)
        self.Layout_Source.setObjectName(u"Layout_Source")
        self.Label_Source = LabelBase(self.groupBox_Settings)
        self.Label_Source.setObjectName(u"Label_Source")

        self.Layout_Source.addWidget(self.Label_Source)

        self.ComboBox_Source = ComboBoxBase(self.groupBox_Settings)
        self.ComboBox_Source.setObjectName(u"ComboBox_Source")
        sizePolicy.setHeightForWidth(self.ComboBox_Source.sizePolicy().hasHeightForWidth())
        self.ComboBox_Source.setSizePolicy(sizePolicy)

        self.Layout_Source.addWidget(self.ComboBox_Source)


        self.gridLayout_34.addLayout(self.Layout_Source, 0, 2, 1, 1)

        self.StackedWidget_TypeParams = QStackedWidget(self.groupBox_Settings)
        self.StackedWidget_TypeParams.setObjectName(u"StackedWidget_TypeParams")
        self.Page1 = QWidget()
        self.Page1.setObjectName(u"Page1")
        self.horizontalLayout_9 = QHBoxLayout(self.Page1)
        self.horizontalLayout_9.setSpacing(21)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.Layout_Role = QHBoxLayout()
        self.Layout_Role.setSpacing(12)
        self.Layout_Role.setObjectName(u"Layout_Role")
        self.Label_Role = LabelBase(self.Page1)
        self.Label_Role.setObjectName(u"Label_Role")

        self.Layout_Role.addWidget(self.Label_Role)

        self.ComboBox_Role = ComboBoxBase(self.Page1)
        self.ComboBox_Role.setObjectName(u"ComboBox_Role")
        sizePolicy.setHeightForWidth(self.ComboBox_Role.sizePolicy().hasHeightForWidth())
        self.ComboBox_Role.setSizePolicy(sizePolicy)

        self.Layout_Role.addWidget(self.ComboBox_Role)

        self.Button_ManageRole = HollowButton(self.Page1)
        self.Button_ManageRole.setObjectName(u"Button_ManageRole")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Button_ManageRole.sizePolicy().hasHeightForWidth())
        self.Button_ManageRole.setSizePolicy(sizePolicy1)

        self.Layout_Role.addWidget(self.Button_ManageRole)


        self.horizontalLayout_9.addLayout(self.Layout_Role)

        self.StackedWidget_TypeParams.addWidget(self.Page1)
        self.Page2 = QWidget()
        self.Page2.setObjectName(u"Page2")
        self.horizontalLayout_10 = QHBoxLayout(self.Page2)
        self.horizontalLayout_10.setSpacing(21)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.Layout_AssistantID = QHBoxLayout()
        self.Layout_AssistantID.setSpacing(12)
        self.Layout_AssistantID.setObjectName(u"Layout_AssistantID")
        self.Label_AssistantID = LabelBase(self.Page2)
        self.Label_AssistantID.setObjectName(u"Label_AssistantID")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.Label_AssistantID.sizePolicy().hasHeightForWidth())
        self.Label_AssistantID.setSizePolicy(sizePolicy2)

        self.Layout_AssistantID.addWidget(self.Label_AssistantID)

        self.LineEdit_AssistantID = LineEditBase(self.Page2)
        self.LineEdit_AssistantID.setObjectName(u"LineEdit_AssistantID")

        self.Layout_AssistantID.addWidget(self.LineEdit_AssistantID)


        self.horizontalLayout_10.addLayout(self.Layout_AssistantID)

        self.StackedWidget_TypeParams.addWidget(self.Page2)

        self.gridLayout_34.addWidget(self.StackedWidget_TypeParams, 0, 3, 1, 1)

        self.toolBox_AdvanceSettings = ToolBoxBase(self.groupBox_Settings)
        self.toolBox_AdvanceSettings.setObjectName(u"toolBox_AdvanceSettings")
        self.ToolPage = WidgetBase()
        self.ToolPage.setObjectName(u"ToolPage")
        self.ToolPage.setGeometry(QRect(0, 0, 774, 69))
        self.gridLayout_35 = QGridLayout(self.ToolPage)
        self.gridLayout_35.setObjectName(u"gridLayout_35")
        self.gridLayout_35.setHorizontalSpacing(21)
        self.gridLayout_35.setVerticalSpacing(12)
        self.gridLayout_35.setContentsMargins(0, 9, 0, 0)
        self.Layout_rag = QHBoxLayout()
        self.Layout_rag.setSpacing(12)
        self.Layout_rag.setObjectName(u"Layout_rag")
        self.Label_rag = LabelBase(self.ToolPage)
        self.Label_rag.setObjectName(u"Label_rag")

        self.Layout_rag.addWidget(self.Label_rag)

        self.LineEdit_rag = LineEditBase(self.ToolPage)
        self.LineEdit_rag.setObjectName(u"LineEdit_rag")

        self.Layout_rag.addWidget(self.LineEdit_rag)


        self.gridLayout_35.addLayout(self.Layout_rag, 0, 0, 1, 1)

        self.toolBox_AdvanceSettings.addItem(self.ToolPage, u"Page 1")

        self.gridLayout_34.addWidget(self.toolBox_AdvanceSettings, 1, 0, 1, 4)


        self.gridLayout_3.addWidget(self.groupBox_Settings, 0, 0, 1, 1)

        self.dockWidget_Top.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(Qt.TopDockWidgetArea, self.dockWidget_Top)
        self.dockWidget_Left = DockWidgetBase(MainWindow)
        self.dockWidget_Left.setObjectName(u"dockWidget_Left")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout = QGridLayout(self.dockWidgetContents)
        self.gridLayout.setSpacing(12)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(12, 0, 12, 12)
        self.ListWidget_Conversation = ListBase(self.dockWidgetContents)
        self.ListWidget_Conversation.setObjectName(u"ListWidget_Conversation")

        self.gridLayout.addWidget(self.ListWidget_Conversation, 0, 0, 1, 1)

        self.Button_ClearConversations = HollowButton(self.dockWidgetContents)
        self.Button_ClearConversations.setObjectName(u"Button_ClearConversations")

        self.gridLayout.addWidget(self.Button_ClearConversations, 1, 0, 1, 1)

        self.Button_CreateConversation = HollowButton(self.dockWidgetContents)
        self.Button_CreateConversation.setObjectName(u"Button_CreateConversation")

        self.gridLayout.addWidget(self.Button_CreateConversation, 2, 0, 1, 1)

        self.dockWidget_Left.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_Left)
        self.dockWidget_Right = DockWidgetBase(MainWindow)
        self.dockWidget_Right.setObjectName(u"dockWidget_Right")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.gridLayout_2 = QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_2.setSpacing(12)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(12, 0, 12, 12)
        self.splitter = QSplitter(self.dockWidgetContents_2)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setStyleSheet(u"QSplitter {\n"
"	background: transparent;\n"
"	border: none;\n"
"}\n"
"\n"
"QSplitter::handle {\n"
"	background: transparent;\n"
"	border: none;\n"
"}")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.MessageBrowser = ChatWidgetBase(self.splitter)
        self.MessageBrowser.setObjectName(u"MessageBrowser")
        self.MessageBrowser.setMinimumSize(QSize(0, 123))
        self.MessageBrowser.setFrameShape(QFrame.StyledPanel)
        self.MessageBrowser.setFrameShadow(QFrame.Raised)
        self.splitter.addWidget(self.MessageBrowser)
        self.TextEdit_Input = TextEditBase(self.splitter)
        self.TextEdit_Input.setObjectName(u"TextEdit_Input")
        self.splitter.addWidget(self.TextEdit_Input)

        self.gridLayout_2.addWidget(self.splitter, 0, 0, 1, 1)

        self.Button_Load = HollowButton(self.dockWidgetContents_2)
        self.Button_Load.setObjectName(u"Button_Load")

        self.gridLayout_2.addWidget(self.Button_Load, 1, 0, 1, 1)

        self.StackedWidget_SendAndStop = QStackedWidget(self.dockWidgetContents_2)
        self.StackedWidget_SendAndStop.setObjectName(u"StackedWidget_SendAndStop")
        sizePolicy2.setHeightForWidth(self.StackedWidget_SendAndStop.sizePolicy().hasHeightForWidth())
        self.StackedWidget_SendAndStop.setSizePolicy(sizePolicy2)
        self.StackedWidgetPage_Send = QWidget()
        self.StackedWidgetPage_Send.setObjectName(u"StackedWidgetPage_Send")
        self.gridLayout_36 = QGridLayout(self.StackedWidgetPage_Send)
        self.gridLayout_36.setObjectName(u"gridLayout_36")
        self.gridLayout_36.setHorizontalSpacing(12)
        self.gridLayout_36.setVerticalSpacing(0)
        self.gridLayout_36.setContentsMargins(0, 0, 0, 0)
        self.Button_Send = HollowButton(self.StackedWidgetPage_Send)
        self.Button_Send.setObjectName(u"Button_Send")

        self.gridLayout_36.addWidget(self.Button_Send, 0, 0, 1, 1)

        self.Button_Test = HollowButton(self.StackedWidgetPage_Send)
        self.Button_Test.setObjectName(u"Button_Test")

        self.gridLayout_36.addWidget(self.Button_Test, 0, 1, 1, 1)

        self.StackedWidget_SendAndStop.addWidget(self.StackedWidgetPage_Send)
        self.StackedWidgetPage_Stop = QWidget()
        self.StackedWidgetPage_Stop.setObjectName(u"StackedWidgetPage_Stop")
        self.gridLayout_37 = QGridLayout(self.StackedWidgetPage_Stop)
        self.gridLayout_37.setSpacing(0)
        self.gridLayout_37.setObjectName(u"gridLayout_37")
        self.gridLayout_37.setContentsMargins(0, 0, 0, 0)
        self.Button_Stop = HollowButton(self.StackedWidgetPage_Stop)
        self.Button_Stop.setObjectName(u"Button_Stop")

        self.gridLayout_37.addWidget(self.Button_Stop, 0, 0, 1, 1)

        self.StackedWidget_SendAndStop.addWidget(self.StackedWidgetPage_Stop)

        self.gridLayout_2.addWidget(self.StackedWidget_SendAndStop, 2, 0, 1, 1)

        self.dockWidget_Right.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_Right)

        self.retranslateUi(MainWindow)

        self.StackedWidget_TypeParams.setCurrentIndex(0)
        self.toolBox_AdvanceSettings.setCurrentIndex(0)
        self.StackedWidget_SendAndStop.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox_Settings.setTitle(QCoreApplication.translate("MainWindow", u"GroupBox", None))
        self.Label_Type.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Label_Model.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Label_Source.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Label_Role.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Button_ManageRole.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Label_AssistantID.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.Label_rag.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.toolBox_AdvanceSettings.setItemText(self.toolBox_AdvanceSettings.indexOf(self.ToolPage), QCoreApplication.translate("MainWindow", u"Page 1", None))
        self.Button_ClearConversations.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_CreateConversation.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_Load.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_Send.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_Test.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.Button_Stop.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
    # retranslateUi