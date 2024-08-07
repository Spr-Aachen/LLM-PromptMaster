# -*- coding: utf-8 -*-

from PySide6.QtCore import QSize
from PySide6.QtWidgets import *

from components.Components import *


class Ui_Window(object):
    def setupUi(self, Window):
        if not Window.objectName():
            Window.setObjectName(u"Window")
        Window.resize(848, 684)

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
"	border-image: url(:/CheckBox_Icon/images/Moon.png);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"	border-image: url(:/CheckBox_Icon/images/Sun.png);\n"
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
        self.Button_Minimize_Window = QPushButton(self.Frame_Top_Control_Window)
        self.Button_Minimize_Window.setObjectName(u"Button_Minimize_Window")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Button_Minimize_Window.sizePolicy().hasHeightForWidth())
        self.Button_Minimize_Window.setSizePolicy(sizePolicy)
        self.Button_Minimize_Window.setStyleSheet(u"QPushButton {\n"
"	image: url(:/Button_Icon/images/Dash.png);\n"
"	background-color: transparent;\n"
"	padding: 6.6px;\n"
"	border-width: 0px;\n"
"	border-radius: 0px;\n"
"	border-style: solid;\n"
"	border-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgba(123, 123, 123, 123);\n"
"}")

        self.horizontalLayout_12.addWidget(self.Button_Minimize_Window)

        self.Button_Maximize_Window = QPushButton(self.Frame_Top_Control_Window)
        self.Button_Maximize_Window.setObjectName(u"Button_Maximize_Window")
        sizePolicy.setHeightForWidth(self.Button_Maximize_Window.sizePolicy().hasHeightForWidth())
        self.Button_Maximize_Window.setSizePolicy(sizePolicy)
        self.Button_Maximize_Window.setStyleSheet(u"QPushButton {\n"
"	image: url(:/Button_Icon/images/FullScreen.png);\n"
"	background-color: transparent;\n"
"	padding: 6.6px;\n"
"	border-width: 0px;\n"
"	border-radius: 0px;\n"
"	border-style: solid;\n"
"	border-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgba(123, 123, 123, 123);\n"
"}")

        self.horizontalLayout_12.addWidget(self.Button_Maximize_Window)

        self.Button_Close_Window = QPushButton(self.Frame_Top_Control_Window)
        self.Button_Close_Window.setObjectName(u"Button_Close_Window")
        sizePolicy.setHeightForWidth(self.Button_Close_Window.sizePolicy().hasHeightForWidth())
        self.Button_Close_Window.setSizePolicy(sizePolicy)
        self.Button_Close_Window.setStyleSheet(u"QPushButton {\n"
"	image: url(:/Button_Icon/images/X.png);\n"
"	background-color: transparent;\n"
"	padding: 6.6px;\n"
"	border-width: 0px;\n"
"	border-radius: 0px;\n"
"	border-style: solid;\n"
"	border-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgba(210, 123, 123, 210);\n"
"}")

        self.horizontalLayout_12.addWidget(self.Button_Close_Window)

        self.horizontalLayout_11.addWidget(self.Frame_Top_Control_Window)

        self.horizontalLayout_30.addWidget(self.Frame_Top)

        # Top area
        self.Label_Protocal = LabelBase()
        self.ComboBox_Protocol = ComboBoxBase()
        self.ComboBox_Protocol.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        Layout_Protocal = QHBoxLayout()
        Layout_Protocal.addWidget(self.Label_Protocal)
        Layout_Protocal.addWidget(self.ComboBox_Protocol)

        self.Label_ip = LabelBase()
        self.LineEdit_ip = LineEditBase()
        self.LineEdit_ip.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        Layout_ip = QHBoxLayout()
        Layout_ip.addWidget(self.Label_ip)
        Layout_ip.addWidget(self.LineEdit_ip)

        self.Label_port = LabelBase()
        self.SpinBox_port = SpinBoxBase()
        self.SpinBox_port.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        Layout_port = QHBoxLayout()
        Layout_port.addWidget(self.Label_port)
        Layout_port.addWidget(self.SpinBox_port)

        self.Label_Type = LabelBase()
        self.ComboBox_Type = ComboBoxBase()
        self.ComboBox_Type.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        Layout_Type = QHBoxLayout()
        Layout_Type.addWidget(self.Label_Type)
        Layout_Type.addWidget(self.ComboBox_Type)

        self.Label_Model = LabelBase()
        self.ComboBox_Model = ComboBoxBase()
        self.ComboBox_Model.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        Layout_Model = QHBoxLayout()
        Layout_Model.addWidget(self.Label_Model)
        Layout_Model.addWidget(self.ComboBox_Model)

        self.Label_Role = LabelBase()
        self.ComboBox_Role = ComboBoxBase()
        self.ComboBox_Role.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.Button_ManageRole = ButtonBase()
        self.Button_ManageRole.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        Layout_Role = QHBoxLayout()
        Layout_Role.addWidget(self.Label_Role)
        Layout_Role.addWidget(self.ComboBox_Role)
        Layout_Role.addWidget(self.Button_ManageRole)

        Layout_Top = QGridLayout()
        Layout_Top.addLayout(Layout_Protocal, 0, 0)
        Layout_Top.addLayout(Layout_ip, 0, 1)
        Layout_Top.addLayout(Layout_port, 0, 2)
        Layout_Top.addLayout(Layout_Type, 1, 0)
        Layout_Top.addLayout(Layout_Model, 1, 1)
        Layout_Top.addLayout(Layout_Role, 1, 2)
        Layout_Top.setContentsMargins(0, 0, 0, 0)
        Layout_Top.setSpacing(12)

        # Right area
        self.TextBrowser = TextBrowserBase()

        self.TextEdit_Input = TextEditBase()

        self.Button_Load = QPushButton()
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

        self.Button_Send = QPushButton()
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
    
        self.Button_Test = QPushButton()
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

        Layout_Right = QGridLayout()
        Layout_Right.addWidget(self.TextBrowser, 0, 0, 5, 2)
        Layout_Right.addWidget(self.TextEdit_Input, 5, 0, 2, 2)
        Layout_Right.addWidget(self.Button_Load, 7, 0, 1, 2)
        Layout_Right.addWidget(self.Button_Send, 8, 0, 1, 1)
        Layout_Right.addWidget(self.Button_Test, 8, 1, 1, 1)
        Layout_Right.setContentsMargins(0, 0, 0, 0)
        Layout_Right.setSpacing(12)

        # Left area
        self.ListWidget_Conversation = ListBase()

        self.Button_ClearConversations = QPushButton()
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

        self.Button_CreateConversation = QPushButton()
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

        Layout_Left = QVBoxLayout()
        Layout_Left.addWidget(self.ListWidget_Conversation)
        Layout_Left.addWidget(self.Button_ClearConversations)
        Layout_Left.addWidget(self.Button_CreateConversation)
        Layout_Left.setContentsMargins(0, 0, 0, 0)
        Layout_Left.setSpacing(12)

        # Combine layouts to ContentWidget
        self.Content = QFrame()
        ContentLayout = QGridLayout(self.Content)
        ContentLayout.addLayout(Layout_Top, 0, 0, 1, 4)
        ContentLayout.addLayout(Layout_Left, 1, 0, 4, 1)
        ContentLayout.addLayout(Layout_Right, 1, 1, 4, 3)
        ContentLayout.setColumnStretch(1, 1)
        ContentLayout.setContentsMargins(12, 12, 12, 12)
        ContentLayout.setSpacing(12)

        # Combine ContentWidget&TitleBar to MainWindow
        Layout = QGridLayout(Window)
        Layout.addWidget(self.TitleBar, 0, 0)
        Layout.addWidget(self.Content, 1, 0)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.setSpacing(0)