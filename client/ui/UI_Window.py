# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, QCoreApplication, QMetaObject, QRect, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import *

from components import *
from view import ChatPage, SettingsPage


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(942, 600)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.titleBar = QFrame(self.centralWidget)
        self.titleBar.setObjectName(u"titleBar")
        self.titleBar.setMinimumSize(QSize(0, 30))
        self.titleBar.setMaximumSize(QSize(16777215, 30))
        self.horizontalLayout_30 = QHBoxLayout(self.titleBar)
        self.horizontalLayout_30.setSpacing(0)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.Frame_Top_Toggle_Menu = QFrame(self.titleBar)
        self.Frame_Top_Toggle_Menu.setObjectName(u"Frame_Top_Toggle_Menu")
        self.Frame_Top_Toggle_Menu.setMinimumSize(QSize(48, 0))
        self.Frame_Top_Toggle_Menu.setMaximumSize(QSize(48, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.Frame_Top_Toggle_Menu)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.Button_Toggle_Menu = QPushButton(self.Frame_Top_Toggle_Menu)
        self.Button_Toggle_Menu.setObjectName(u"Button_Toggle_Menu")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Button_Toggle_Menu.sizePolicy().hasHeightForWidth())
        self.Button_Toggle_Menu.setSizePolicy(sizePolicy)
        self.Button_Toggle_Menu.setStyleSheet(u"QPushButton {\n"
"	/*text-align: center;\n"
"	font-size: 15px;*/\n"
"	image: url(:/Button_Icon/images/icons/Menu.png);\n"
"	/*background-repeat: no-repeat;\n"
"	background-origin: content;\n"
"	background-position: center;*/\n"
"	background-color: transparent;\n"
"	border-width: 1.5px;\n"
"	border-radius: 0px;\n"
"	border-style: solid;\n"
"	border-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"	border-color: rgb(120, 120, 120);\n"
"}\n"
"QPushButton:checked {\n"
"	/*background-color: rgb(45, 45, 45);*/\n"
"}")

        self.verticalLayout_2.addWidget(self.Button_Toggle_Menu)


        self.horizontalLayout_30.addWidget(self.Frame_Top_Toggle_Menu)

        self.Frame_Top = QFrame(self.titleBar)
        self.Frame_Top.setObjectName(u"Frame_Top")
        self.horizontalLayout_11 = QHBoxLayout(self.Frame_Top)
        self.horizontalLayout_11.setSpacing(21)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.HorizontalSpacer_Right_Top = QSpacerItem(587, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.HorizontalSpacer_Right_Top)

        self.CheckBox_SwitchTheme = CheckBoxBase(self.Frame_Top)
        self.CheckBox_SwitchTheme.setObjectName(u"CheckBox_SwitchTheme")

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


        self.gridLayout.addWidget(self.titleBar, 0, 0, 1, 2)

        self.Frame_Menu = QFrame(self.centralWidget)
        self.Frame_Menu.setObjectName(u"Frame_Menu")
        self.Frame_Menu.setMinimumSize(QSize(123, 0))
        self.Frame_Menu.setMaximumSize(QSize(123, 16777215))
        self.verticalLayout_3 = QVBoxLayout(self.Frame_Menu)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 3, 0, 3)
        self.Button_Menu_Home = NavigationButton(self.Frame_Menu)
        self.Button_Menu_Home.setObjectName(u"Button_Menu_Home")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Button_Menu_Home.sizePolicy().hasHeightForWidth())
        self.Button_Menu_Home.setSizePolicy(sizePolicy1)
        self.Button_Menu_Home.setMinimumSize(QSize(0, 48))
        icon = QIcon()
        icon.addFile(u":/Button_Icon/images/icons/Home.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_Menu_Home.setIcon(icon)
        self.Button_Menu_Home.setIconSize(QSize(24, 24))
        self.horizontalLayout_8 = QHBoxLayout(self.Button_Menu_Home)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_3.addWidget(self.Button_Menu_Home)

        self.Button_Menu_Env = NavigationButton(self.Frame_Menu)
        self.Button_Menu_Env.setObjectName(u"Button_Menu_Env")
        sizePolicy1.setHeightForWidth(self.Button_Menu_Env.sizePolicy().hasHeightForWidth())
        self.Button_Menu_Env.setSizePolicy(sizePolicy1)
        self.Button_Menu_Env.setMinimumSize(QSize(0, 48))
        icon1 = QIcon()
        icon1.addFile(u":/Button_Icon/images/icons/Box.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_Menu_Env.setIcon(icon1)
        self.Button_Menu_Env.setIconSize(QSize(24, 24))
        self.horizontalLayout_7 = QHBoxLayout(self.Button_Menu_Env)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_3.addWidget(self.Button_Menu_Env)

        self.VerticalSpacer_Menu = QSpacerItem(20, 522, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.VerticalSpacer_Menu)

        self.Button_Menu_Settings = NavigationButton(self.Frame_Menu)
        self.Button_Menu_Settings.setObjectName(u"Button_Menu_Settings")
        sizePolicy1.setHeightForWidth(self.Button_Menu_Settings.sizePolicy().hasHeightForWidth())
        self.Button_Menu_Settings.setSizePolicy(sizePolicy1)
        self.Button_Menu_Settings.setMinimumSize(QSize(0, 48))
        icon2 = QIcon()
        icon2.addFile(u":/Button_Icon/images/icons/Settings.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.Button_Menu_Settings.setIcon(icon2)
        self.Button_Menu_Settings.setIconSize(QSize(24, 24))
        self.horizontalLayout_9 = QHBoxLayout(self.Button_Menu_Settings)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_3.addWidget(self.Button_Menu_Settings)


        self.gridLayout.addWidget(self.Frame_Menu, 1, 0, 1, 1)

        self.StackedWidget_Pages = QStackedWidget(self.centralWidget)
        self.StackedWidget_Pages.setObjectName(u"StackedWidget_Pages")
        self.Page_Home = QWidget()
        self.Page_Home.setObjectName(u"Page_Home")
        self.gridLayout_2 = QGridLayout(self.Page_Home)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.Label_HomePage = QLabel(self.Page_Home)
        self.Label_HomePage.setObjectName(u"Label_HomePage")
        self.Label_HomePage.setStyleSheet(u"font-size: 33px;")
        self.Label_HomePage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.Label_HomePage, 0, 0, 1, 1)

        self.StackedWidget_Pages.addWidget(self.Page_Home)
        self.Page_Chat = ChatPage()
        self.Page_Chat.setObjectName(u"Page_Chat")
        self.StackedWidget_Pages.addWidget(self.Page_Chat)
        self.Page_Settings = SettingsPage()
        self.Page_Settings.setObjectName(u"Page_Settings")
        self.StackedWidget_Pages.addWidget(self.Page_Settings)

        self.gridLayout.addWidget(self.StackedWidget_Pages, 1, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        self.Button_Toggle_Menu.setToolTip(QCoreApplication.translate("MainWindow", u"\u70b9\u51fb\u4ee5\u5c55\u5f00/\u6298\u53e0\u83dc\u5355", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.Button_Menu_Home.setToolTip(QCoreApplication.translate("MainWindow", u"\u4e3b\u9875", None))
#endif // QT_CONFIG(tooltip)
        self.Button_Menu_Home.setText(QCoreApplication.translate("MainWindow", u"\u4e3b\u9875", None))
#if QT_CONFIG(tooltip)
        self.Button_Menu_Env.setToolTip(QCoreApplication.translate("MainWindow", u"\u73af\u5883\u914d\u7f6e", None))
#endif // QT_CONFIG(tooltip)
        self.Button_Menu_Env.setText(QCoreApplication.translate("MainWindow", u"\u73af\u5883", None))
#if QT_CONFIG(tooltip)
        self.Button_Menu_Settings.setToolTip(QCoreApplication.translate("MainWindow", u"\u5ba2\u6237\u7aef\u8bbe\u7f6e", None))
#endif // QT_CONFIG(tooltip)
        self.Button_Menu_Settings.setText(QCoreApplication.translate("MainWindow", u"\u8bbe\u7f6e", None))
        self.Label_HomePage.setText(QCoreApplication.translate("MainWindow", u"HomePage", None))
    # retranslateUi