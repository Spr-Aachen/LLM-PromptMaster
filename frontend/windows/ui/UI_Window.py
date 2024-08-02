# -*- coding: utf-8 -*-

from PySide6.QtWidgets import *
from QEasyWidgets.ComponentsCustomizer import *


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
        self.ComboBox_Protocol = QComboBox()

        self.LineEdit_ip = QLineEdit()

        self.SpinBox_port = QSpinBox()

        self.ComboBox_Model = QComboBox()

        self.ComboBox_Type = QComboBox()

        Layout_Top = QGridLayout()
        Layout_Top.addWidget(self.ComboBox_Protocol, 0, 1, 1, 2)
        Layout_Top.addWidget(self.LineEdit_ip, 0, 3, 1, 2)
        Layout_Top.addWidget(self.SpinBox_port, 0, 5, 1, 2)
        Layout_Top.addWidget(self.ComboBox_Model, 1, 1, 1, 3)
        Layout_Top.addWidget(self.ComboBox_Type, 1, 4, 1, 3)

        # Right area
        self.TextBrowser = QTextBrowser()

        self.TextEdit_Input = TextEditBase()

        self.Button_Load = QPushButton('Load Questions from File')

        self.Button_Send = QPushButton('Send')
    
        self.Button_Test = QPushButton('Test')

        Layout_Right = QGridLayout()
        Layout_Right.addWidget(self.TextBrowser, 0, 0, 5, 2)
        Layout_Right.addWidget(self.TextEdit_Input, 5, 0, 2, 2)
        Layout_Right.addWidget(self.Button_Load, 7, 0, 1, 2)
        Layout_Right.addWidget(self.Button_Send, 8, 0, 1, 1)
        Layout_Right.addWidget(self.Button_Test, 8, 1, 1, 1)

        # Left area
        self.ListWidget_Conversation = QListWidget()

        self.Button_ClearConversations = QPushButton('Clear All')

        self.Button_CreateConversation = QPushButton('New Conversation')

        Layout_Left = QVBoxLayout()
        Layout_Left.addWidget(self.ListWidget_Conversation)
        Layout_Left.addWidget(self.Button_ClearConversations)
        Layout_Left.addWidget(self.Button_CreateConversation)

        # Combine layouts to ContentWidget
        self.Content = QFrame()
        ContentLayout = QGridLayout(self.Content)
        ContentLayout.addLayout(Layout_Top, 0, 0, 1, 4)
        ContentLayout.addLayout(Layout_Left, 1, 0, 4, 1)
        ContentLayout.addLayout(Layout_Right, 1, 1, 4, 3)
        ContentLayout.setColumnStretch(1, 1)

        # Combine ContentWidget&TitleBar to MainWindow
        Layout = QGridLayout(Window)
        Layout.addWidget(self.TitleBar, 0, 0)
        Layout.addWidget(self.Content, 1, 0)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.setSpacing(0)