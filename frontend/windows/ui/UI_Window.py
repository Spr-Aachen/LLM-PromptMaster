# -*- coding: utf-8 -*-

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtWidgets import *

from components.Components import *


class Ui_Window(object):
    def setupUi(self, Window):
        if not Window.objectName():
            Window.setObjectName(u"Window")
        Window.resize(848, 684)
        self.gridLayout_8 = QGridLayout(Window)
        self.gridLayout_8.setSpacing(0)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.TitleBar = QFrame(Window)
        self.TitleBar.setObjectName(u"TitleBar")
        self.TitleBar.setMinimumSize(QSize(0, 30))
        self.TitleBar.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_30 = QHBoxLayout(self.TitleBar)
        self.horizontalLayout_30.setSpacing(0)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.Frame_Top = QFrame(self.TitleBar)
        self.Frame_Top.setObjectName(u"Frame_Top")
        self.horizontalLayout_11 = QHBoxLayout(self.Frame_Top)
        self.horizontalLayout_11.setSpacing(21)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.HorizontalSpacer_Right_Top = QSpacerItem(587, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.HorizontalSpacer_Right_Top)

        self.CheckBox_SwitchTheme = QCheckBox(self.Frame_Top)
        self.CheckBox_SwitchTheme.setObjectName(u"CheckBox_SwitchTheme")
        self.CheckBox_SwitchTheme.setStyleSheet(u"QCheckBox {\n"
"	font-size: 12px;\n"
"	spacing: 12.3px;\n"
"	background-color: transparent;\n"
"	padding: 0px;\n"
"	border-width: 0px;\n"
"	border-radius: 6px;\n"
"	border-style: solid;\n"
"}\n"
"QCheckBox:hover {\n"
"}\n"
"\n"
"QCheckBox::indicator {\n"
"	width: 16.8px;\n"
"	height: 16.8px;\n"
"    background-color: transparent;\n"
"	padding: 0px;\n"
"	border-width: 0px;\n"
"	border-radius: 6px;\n"
"	border-style: solid;\n"
"}\n"
"QCheckBox::indicator:hover {\n"
"	background-color: rgba(255, 255, 255, 24);\n"
"}\n"
"QCheckBox::indicator:unchecked {\n"
"	border-image: url(:/CheckBox_Icon/images/icons/Moon.png);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"	border-image: url(:/CheckBox_Icon/images/icons/Sun.png);\n"
"}")

        self.horizontalLayout_11.addWidget(self.CheckBox_SwitchTheme)

        self.Frame_Top_Control_Window = QFrame(self.Frame_Top)
        self.Frame_Top_Control_Window.setObjectName(u"Frame_Top_Control_Window")
        self.Frame_Top_Control_Window.setMinimumSize(QSize(144, 0))
        self.Frame_Top_Control_Window.setMaximumSize(QSize(144, 16777215))
        self.horizontalLayout_12 = QHBoxLayout(self.Frame_Top_Control_Window)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.Button_Minimize_Window = ButtonBase(self.Frame_Top_Control_Window)
        self.Button_Minimize_Window.setObjectName(u"Button_Minimize_Window")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Button_Minimize_Window.sizePolicy().hasHeightForWidth())
        self.Button_Minimize_Window.setSizePolicy(sizePolicy)

        self.horizontalLayout_12.addWidget(self.Button_Minimize_Window)

        self.Button_Maximize_Window = ButtonBase(self.Frame_Top_Control_Window)
        self.Button_Maximize_Window.setObjectName(u"Button_Maximize_Window")
        sizePolicy.setHeightForWidth(self.Button_Maximize_Window.sizePolicy().hasHeightForWidth())
        self.Button_Maximize_Window.setSizePolicy(sizePolicy)

        self.horizontalLayout_12.addWidget(self.Button_Maximize_Window)

        self.Button_Close_Window = ButtonBase(self.Frame_Top_Control_Window)
        self.Button_Close_Window.setObjectName(u"Button_Close_Window")
        sizePolicy.setHeightForWidth(self.Button_Close_Window.sizePolicy().hasHeightForWidth())
        self.Button_Close_Window.setSizePolicy(sizePolicy)

        self.horizontalLayout_12.addWidget(self.Button_Close_Window)


        self.horizontalLayout_11.addWidget(self.Frame_Top_Control_Window)


        self.horizontalLayout_30.addWidget(self.Frame_Top)


        self.gridLayout_8.addWidget(self.TitleBar, 0, 0, 1, 1)

        self.Content = QWidget(Window)
        self.Content.setObjectName(u"Content")
        self.gridLayout_2 = QGridLayout(self.Content)
        self.gridLayout_2.setSpacing(12)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(12, 0, 12, 12)
        self.ToolBox = ToolBoxBase(self.Content)
        self.ToolBox.setObjectName(u"ToolBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.ToolBox.sizePolicy().hasHeightForWidth())
        self.ToolBox.setSizePolicy(sizePolicy1)
        self.ToolPage = WidgetBase()
        self.ToolPage.setObjectName(u"ToolPage")
        self.ToolPage.setGeometry(QRect(0, 0, 824, 70))
        self.gridLayout = QGridLayout(self.ToolPage)
        self.gridLayout.setSpacing(12)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 9, 0, 0)
        self.Layout_ip = QHBoxLayout()
        self.Layout_ip.setObjectName(u"Layout_ip")
        self.Label_ip = QLabel(self.ToolPage)
        self.Label_ip.setObjectName(u"Label_ip")

        self.Layout_ip.addWidget(self.Label_ip)

        self.LineEdit_ip = LineEditBase(self.ToolPage)
        self.LineEdit_ip.setObjectName(u"LineEdit_ip")

        self.Layout_ip.addWidget(self.LineEdit_ip)


        self.gridLayout.addLayout(self.Layout_ip, 0, 1, 1, 1)

        self.Layout_port = QHBoxLayout()
        self.Layout_port.setObjectName(u"Layout_port")
        self.Label_port = QLabel(self.ToolPage)
        self.Label_port.setObjectName(u"Label_port")

        self.Layout_port.addWidget(self.Label_port)

        self.SpinBox_port = SpinBoxBase(self.ToolPage)
        self.SpinBox_port.setObjectName(u"SpinBox_port")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.SpinBox_port.sizePolicy().hasHeightForWidth())
        self.SpinBox_port.setSizePolicy(sizePolicy2)

        self.Layout_port.addWidget(self.SpinBox_port)


        self.gridLayout.addLayout(self.Layout_port, 0, 2, 1, 1)

        self.Layout_Type = QHBoxLayout()
        self.Layout_Type.setObjectName(u"Layout_Type")
        self.Label_Type = QLabel(self.ToolPage)
        self.Label_Type.setObjectName(u"Label_Type")

        self.Layout_Type.addWidget(self.Label_Type)

        self.ComboBox_Type = ComboBoxBase(self.ToolPage)
        self.ComboBox_Type.setObjectName(u"ComboBox_Type")
        sizePolicy2.setHeightForWidth(self.ComboBox_Type.sizePolicy().hasHeightForWidth())
        self.ComboBox_Type.setSizePolicy(sizePolicy2)

        self.Layout_Type.addWidget(self.ComboBox_Type)


        self.gridLayout.addLayout(self.Layout_Type, 1, 0, 1, 1)

        self.Layout_Protocal = QHBoxLayout()
        self.Layout_Protocal.setObjectName(u"Layout_Protocal")
        self.Label_Protocal = QLabel(self.ToolPage)
        self.Label_Protocal.setObjectName(u"Label_Protocal")

        self.Layout_Protocal.addWidget(self.Label_Protocal)

        self.ComboBox_Protocol = ComboBoxBase(self.ToolPage)
        self.ComboBox_Protocol.setObjectName(u"ComboBox_Protocol")
        sizePolicy2.setHeightForWidth(self.ComboBox_Protocol.sizePolicy().hasHeightForWidth())
        self.ComboBox_Protocol.setSizePolicy(sizePolicy2)

        self.Layout_Protocal.addWidget(self.ComboBox_Protocol)


        self.gridLayout.addLayout(self.Layout_Protocal, 0, 0, 1, 1)

        self.StackedWidget_TypeParams = QStackedWidget(self.ToolPage)
        self.StackedWidget_TypeParams.setObjectName(u"StackedWidget_TypeParams")
        self.Page1 = QWidget()
        self.Page1.setObjectName(u"Page1")
        self.horizontalLayout = QHBoxLayout(self.Page1)
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.Layout_Model = QHBoxLayout()
        self.Layout_Model.setObjectName(u"Layout_Model")
        self.Label_Model = QLabel(self.Page1)
        self.Label_Model.setObjectName(u"Label_Model")

        self.Layout_Model.addWidget(self.Label_Model)

        self.ComboBox_Model = ComboBoxBase(self.Page1)
        self.ComboBox_Model.setObjectName(u"ComboBox_Model")
        sizePolicy2.setHeightForWidth(self.ComboBox_Model.sizePolicy().hasHeightForWidth())
        self.ComboBox_Model.setSizePolicy(sizePolicy2)

        self.Layout_Model.addWidget(self.ComboBox_Model)


        self.horizontalLayout.addLayout(self.Layout_Model)

        self.Layout_Role = QHBoxLayout()
        self.Layout_Role.setObjectName(u"Layout_Role")
        self.Label_Role = QLabel(self.Page1)
        self.Label_Role.setObjectName(u"Label_Role")

        self.Layout_Role.addWidget(self.Label_Role)

        self.ComboBox_Role = ComboBoxBase(self.Page1)
        self.ComboBox_Role.setObjectName(u"ComboBox_Role")
        sizePolicy2.setHeightForWidth(self.ComboBox_Role.sizePolicy().hasHeightForWidth())
        self.ComboBox_Role.setSizePolicy(sizePolicy2)

        self.Layout_Role.addWidget(self.ComboBox_Role)

        self.Button_ManageRole = ButtonBase(self.Page1)
        self.Button_ManageRole.setObjectName(u"Button_ManageRole")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.Button_ManageRole.sizePolicy().hasHeightForWidth())
        self.Button_ManageRole.setSizePolicy(sizePolicy3)

        self.Layout_Role.addWidget(self.Button_ManageRole)


        self.horizontalLayout.addLayout(self.Layout_Role)

        self.StackedWidget_TypeParams.addWidget(self.Page1)
        self.Page2 = QWidget()
        self.Page2.setObjectName(u"Page2")
        self.horizontalLayout_2 = QHBoxLayout(self.Page2)
        self.horizontalLayout_2.setSpacing(12)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.Layout_AssistantID = QHBoxLayout()
        self.Layout_AssistantID.setObjectName(u"Layout_AssistantID")
        self.Label_AssistantID = QLabel(self.Page2)
        self.Label_AssistantID.setObjectName(u"Label_AssistantID")

        self.Layout_AssistantID.addWidget(self.Label_AssistantID)

        self.LineEdit_AssistantID = LineEditBase(self.Page2)
        self.LineEdit_AssistantID.setObjectName(u"LineEdit_AssistantID")

        self.Layout_AssistantID.addWidget(self.LineEdit_AssistantID)


        self.horizontalLayout_2.addLayout(self.Layout_AssistantID)

        self.horizontalSpacer_AssistantID = QSpacerItem(263, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_AssistantID)

        self.StackedWidget_TypeParams.addWidget(self.Page2)

        self.gridLayout.addWidget(self.StackedWidget_TypeParams, 1, 1, 1, 2)

        self.ToolBox.addItem(self.ToolPage, u"Page 1")

        self.gridLayout_2.addWidget(self.ToolBox, 0, 0, 1, 2)

        self.Content_Left = QWidget(self.Content)
        self.Content_Left.setObjectName(u"Content_Left")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.Content_Left.sizePolicy().hasHeightForWidth())
        self.Content_Left.setSizePolicy(sizePolicy4)
        self.Layout_Left = QGridLayout(self.Content_Left)
        self.Layout_Left.setSpacing(12)
        self.Layout_Left.setObjectName(u"Layout_Left")
        self.Layout_Left.setContentsMargins(0, 0, 0, 0)
        self.ListWidget_Conversation = ListBase(self.Content_Left)
        self.ListWidget_Conversation.setObjectName(u"ListWidget_Conversation")

        self.Layout_Left.addWidget(self.ListWidget_Conversation, 0, 0, 1, 1)

        self.Button_ClearConversations = QPushButton(self.Content_Left)
        self.Button_ClearConversations.setObjectName(u"Button_ClearConversations")
        self.Button_ClearConversations.setStyleSheet(u"QPushButton {\n"
"	text-align: center;\n"
"	font-size: 12px;\n"
"	background-color: transparent;\n"
"	padding: 6.6px;\n"
"	border-width: 1.2px;\n"
"	border-style: solid;\n"
"	border-color: rgb(90, 90, 90);\n"
"}\n"
"QPushButton:hover {\n"
"	border-color: rgb(120, 120, 120);\n"
"}")

        self.Layout_Left.addWidget(self.Button_ClearConversations, 1, 0, 1, 1)

        self.Button_CreateConversation = QPushButton(self.Content_Left)
        self.Button_CreateConversation.setObjectName(u"Button_CreateConversation")
        self.Button_CreateConversation.setStyleSheet(u"QPushButton {\n"
"	text-align: center;\n"
"	font-size: 12px;\n"
"	background-color: transparent;\n"
"	padding: 6.6px;\n"
"	border-width: 1.2px;\n"
"	border-style: solid;\n"
"	border-color: rgb(90, 90, 90);\n"
"}\n"
"QPushButton:hover {\n"
"	border-color: rgb(120, 120, 120);\n"
"}")

        self.Layout_Left.addWidget(self.Button_CreateConversation, 2, 0, 1, 1)


        self.gridLayout_2.addWidget(self.Content_Left, 1, 0, 1, 1)

        self.Content_Right = QWidget(self.Content)
        self.Content_Right.setObjectName(u"Content_Right")
        self.Layout_Right = QGridLayout(self.Content_Right)
        self.Layout_Right.setSpacing(12)
        self.Layout_Right.setObjectName(u"Layout_Right")
        self.Layout_Right.setContentsMargins(0, 0, 0, 0)
        self.Button_Load = QPushButton(self.Content_Right)
        self.Button_Load.setObjectName(u"Button_Load")
        self.Button_Load.setStyleSheet(u"QPushButton {\n"
"	text-align: center;\n"
"	font-size: 12px;\n"
"	background-color: transparent;\n"
"	padding: 6.6px;\n"
"	border-width: 1.2px;\n"
"	border-style: solid;\n"
"	border-color: rgb(90, 90, 90);\n"
"}\n"
"QPushButton:hover {\n"
"	border-color: rgb(120, 120, 120);\n"
"}")

        self.Layout_Right.addWidget(self.Button_Load, 1, 0, 1, 2)

        self.splitter = QSplitter(self.Content_Right)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setStyleSheet(u"QSplitter {\n"
"	background-color: transparent;\n"
"}\n"
"\n"
"QSplitter::handle {\n"
"	background-color: transparent;\n"
"}\n"
"QSplitter::handle:pressed {\n"
"	background-color: grey;\n"
"}")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(12)
        self.splitter.setChildrenCollapsible(False)
        self.TextBrowser = TextBrowserBase(self.splitter)
        self.TextBrowser.setObjectName(u"TextBrowser")
        self.splitter.addWidget(self.TextBrowser)
        self.TextEdit_Input = TextEditBase(self.splitter)
        self.TextEdit_Input.setObjectName(u"TextEdit_Input")
        self.splitter.addWidget(self.TextEdit_Input)

        self.Layout_Right.addWidget(self.splitter, 0, 0, 1, 2)

        self.StackedWidget_SendAndStop = QStackedWidget(self.Content_Right)
        self.StackedWidget_SendAndStop.setObjectName(u"StackedWidget_SendAndStop")
        sizePolicy1.setHeightForWidth(self.StackedWidget_SendAndStop.sizePolicy().hasHeightForWidth())
        self.StackedWidget_SendAndStop.setSizePolicy(sizePolicy1)
        self.StackedWidgetPage_Send = QWidget()
        self.StackedWidgetPage_Send.setObjectName(u"StackedWidgetPage_Send")
        self.gridLayout_3 = QGridLayout(self.StackedWidgetPage_Send)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(12)
        self.gridLayout_3.setVerticalSpacing(0)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.Button_Send = QPushButton(self.StackedWidgetPage_Send)
        self.Button_Send.setObjectName(u"Button_Send")
        self.Button_Send.setStyleSheet(u"QPushButton {\n"
"	text-align: center;\n"
"	font-size: 12px;\n"
"	background-color: transparent;\n"
"	padding: 6.6px;\n"
"	border-width: 1.2px;\n"
"	border-style: solid;\n"
"	border-color: rgb(90, 90, 90);\n"
"}\n"
"QPushButton:hover {\n"
"	border-color: rgb(120, 120, 120);\n"
"}")

        self.gridLayout_3.addWidget(self.Button_Send, 0, 0, 1, 1)

        self.Button_Test = QPushButton(self.StackedWidgetPage_Send)
        self.Button_Test.setObjectName(u"Button_Test")
        self.Button_Test.setStyleSheet(u"QPushButton {\n"
"	text-align: center;\n"
"	font-size: 12px;\n"
"	background-color: transparent;\n"
"	padding: 6.6px;\n"
"	border-width: 1.2px;\n"
"	border-style: solid;\n"
"	border-color: rgb(90, 90, 90);\n"
"}\n"
"QPushButton:hover {\n"
"	border-color: rgb(120, 120, 120);\n"
"}")

        self.gridLayout_3.addWidget(self.Button_Test, 0, 1, 1, 1)

        self.StackedWidget_SendAndStop.addWidget(self.StackedWidgetPage_Send)
        self.StackedWidgetPage_Stop = QWidget()
        self.StackedWidgetPage_Stop.setObjectName(u"StackedWidgetPage_Stop")
        self.gridLayout_4 = QGridLayout(self.StackedWidgetPage_Stop)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.Button_Stop = QPushButton(self.StackedWidgetPage_Stop)
        self.Button_Stop.setObjectName(u"Button_Stop")
        self.Button_Stop.setStyleSheet(u"QPushButton {\n"
"	text-align: center;\n"
"	font-size: 12px;\n"
"	background-color: transparent;\n"
"	padding: 6.6px;\n"
"	border-width: 1.2px;\n"
"	border-style: solid;\n"
"	border-color: rgb(90, 90, 90);\n"
"}\n"
"QPushButton:hover {\n"
"	border-color: rgb(120, 120, 120);\n"
"}")

        self.gridLayout_4.addWidget(self.Button_Stop, 0, 0, 1, 1)

        self.StackedWidget_SendAndStop.addWidget(self.StackedWidgetPage_Stop)

        self.Layout_Right.addWidget(self.StackedWidget_SendAndStop, 3, 0, 1, 2)


        self.gridLayout_2.addWidget(self.Content_Right, 1, 1, 1, 1)


        self.gridLayout_8.addWidget(self.Content, 1, 0, 1, 1)


        self.retranslateUi(Window)

        self.ToolBox.setCurrentIndex(0)
        self.StackedWidget_TypeParams.setCurrentIndex(0)
        self.StackedWidget_SendAndStop.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Window)
    # setupUi

    def retranslateUi(self, Window):
        Window.setWindowTitle(QCoreApplication.translate("Window", u"Window", None))
        self.Label_ip.setText(QCoreApplication.translate("Window", u"TextLabel", None))
        self.Label_port.setText(QCoreApplication.translate("Window", u"TextLabel", None))
        self.Label_Type.setText(QCoreApplication.translate("Window", u"TextLabel", None))
        self.Label_Protocal.setText(QCoreApplication.translate("Window", u"TextLabel", None))
        self.Label_Model.setText(QCoreApplication.translate("Window", u"TextLabel", None))
        self.Label_Role.setText(QCoreApplication.translate("Window", u"TextLabel", None))
        self.Button_ManageRole.setText(QCoreApplication.translate("Window", u"PushButton", None))
        self.Label_AssistantID.setText(QCoreApplication.translate("Window", u"TextLabel", None))
        self.ToolBox.setItemText(self.ToolBox.indexOf(self.ToolPage), QCoreApplication.translate("Window", u"Page 1", None))
        self.Button_ClearConversations.setText(QCoreApplication.translate("Window", u"PushButton", None))
        self.Button_CreateConversation.setText(QCoreApplication.translate("Window", u"PushButton", None))
        self.Button_Load.setText(QCoreApplication.translate("Window", u"PushButton", None))
        self.Button_Send.setText(QCoreApplication.translate("Window", u"PushButton", None))
        self.Button_Test.setText(QCoreApplication.translate("Window", u"PushButton", None))
        self.Button_Stop.setText(QCoreApplication.translate("Window", u"PushButton", None))
    # retranslateUi