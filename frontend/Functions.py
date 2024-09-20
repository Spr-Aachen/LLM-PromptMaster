import os
import platform
from typing import Union, Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread, QPoint
from PySide6.QtCore import QCoreApplication as QCA
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets.Windows import *
from QEasyWidgets.Components import *

from components.Components import *
from windows.Windows import *

##############################################################################################################################

# Where to store custom signals
class CustomSignals_Functions(QObject):
    '''
    Set up signals for functions
    '''
    # Run task
    Signal_ExecuteTask = Signal(tuple)

    # Monitor task
    Signal_TaskStatus = Signal(str, str)

    # Force exit
    Signal_ForceQuit = Signal()


FunctionSignals = CustomSignals_Functions()

##############################################################################################################################

def Function_ConfigureCheckBox(
    CheckBox: QCheckBox,
    CheckedText: Optional[str] = None,
    CheckedEvents: list = [],
    UncheckedText: Optional[str] = None,
    UncheckedEvents: list = [],
    TakeEffect: bool = False
):
    '''
    Function to configure checkbox
    '''
    if CheckedText is not None:
        CheckedEvents.append(lambda: CheckBox.setText(CheckedText))
    if UncheckedText is not None:
        UncheckedEvents.append(lambda: CheckBox.setText(UncheckedText))

    CheckBox.toggled.connect(
        lambda IsChecked: QFunc.RunEvents(CheckedEvents if IsChecked else UncheckedEvents)
    )

    QFunc.RunEvents(CheckedEvents) if TakeEffect and CheckBox.isChecked() else None
    QFunc.RunEvents(UncheckedEvents) if TakeEffect and not CheckBox.isChecked() else None

##############################################################################################################################

def Function_AnimateStackedWidget(
    StackedWidget: QStackedWidget,
    TargetIndex: int = 0,
    Duration: int = 210
):
    '''
    Function to animate stackedwidget
    '''
    OriginalWidget = StackedWidget.currentWidget()
    OriginalGeometry = OriginalWidget.geometry()

    WidgetAnimation = QFunc.Function_SetWidgetPosAnimation(OriginalWidget, Duration)
    WidgetAnimation.finished.connect(
        lambda: StackedWidget.setCurrentIndex(TargetIndex),
        type = Qt.QueuedConnection
    )
    WidgetAnimation.finished.connect(
        lambda: OriginalWidget.setGeometry(OriginalGeometry),
        type = Qt.QueuedConnection
    )
    WidgetAnimation.start() if StackedWidget.currentIndex() != TargetIndex else None


def Function_AnimateFrame(
    Frame: QWidget,
    MinWidth: Optional[int] = None,
    MaxWidth: Optional[int] = None,
    MinHeight: Optional[int] = None,
    MaxHeight: Optional[int] = None,
    Duration: int = 210,
    Mode: str = "Toggle",
    SupportSplitter: bool = False
):
    '''
    Function to animate frame
    '''
    def ExtendFrame():
        QFunc.Function_SetWidgetSizeAnimation(Frame, MaxWidth, None, Duration, SupportSplitter).start() if MaxWidth not in (None, Frame.width()) else None
        QFunc.Function_SetWidgetSizeAnimation(Frame, None, MaxHeight, Duration, SupportSplitter).start() if MaxHeight not in (None, Frame.height()) else None

    def ReduceFrame():
        QFunc.Function_SetWidgetSizeAnimation(Frame, MinWidth, None, Duration, SupportSplitter).start() if MinWidth not in (None, Frame.width()) else None
        QFunc.Function_SetWidgetSizeAnimation(Frame, None, MinHeight, Duration, SupportSplitter).start() if MinHeight not in (None, Frame.height()) else None

    if Mode == "Extend":
        ExtendFrame()
    if Mode == "Reduce":
        ReduceFrame()
    if Mode == "Toggle":
        ExtendFrame() if Frame.width() == MinWidth or Frame.height() == MinHeight else ReduceFrame()


def Function_AnimateProgressBar(
    ProgressBar: QProgressBar,
    MinValue: int = 0,
    MaxValue: int = 100,
    DisplayValue: bool = False,
    IsTaskAlive: bool = False
):
    '''
    Function to animate progressbar
    '''
    ProgressBar.setTextVisible(DisplayValue)
    ProgressBar.setRange(MinValue, MaxValue)
    ProgressBar.setValue(MinValue)

    if IsTaskAlive == True:
        ProgressBar.setRange(0, 0)
        #QApplication.processEvents()
    else:
        ProgressBar.setRange(MinValue, MaxValue)
        ProgressBar.setValue(MaxValue)

##############################################################################################################################

def Function_SetWidgetValue(
    Widget: QWidget,
    Config: QFunc.ManageConfig,
    Section: str = ...,
    Option: str = ...,
    Value = ...,
    Times: Union[int, float] = 1,
    SetPlaceholderText: bool = False,
    PlaceholderText: Optional[str] = None
):
    if isinstance(Widget, (QLineEdit, LineEditBase, QTextEdit, TextEditBase, QPlainTextEdit)):
        QFunc.Function_SetText(Widget, Value, SetPlaceholderText = SetPlaceholderText, PlaceholderText = PlaceholderText)
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.textChanged.connect(EditConfig)
            EditConfig(Value)

    if isinstance(Widget, (QComboBox, ComboBoxBase)):
        Widget.setCurrentText(str(Value))
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.currentTextChanged.connect(EditConfig)
            EditConfig(Value)

    if isinstance(Widget, (QSlider, QSpinBox, SpinBoxBase)):
        Widget.setValue(int(eval(str(Value)) * Times))
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(eval(str(Value)) / Times))
        if Config is not None:
            Widget.valueChanged.connect(EditConfig)
            EditConfig(Value)

    if isinstance(Widget, (QDoubleSpinBox, DoubleSpinBoxBase)):
        Widget.setValue(float(eval(str(Value)) * Times))
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(eval(str(Value)) / Times))
        if Config is not None:
            Widget.valueChanged.connect(EditConfig)
            EditConfig(Value)

    if isinstance(Widget, (QCheckBox, QRadioButton)):
        Widget.setChecked(eval(str(Value)))
        def EditConfig(Value):
            Config.EditConfig(Section, Option, str(Value))
        if Config is not None:
            Widget.toggled.connect(EditConfig)
            EditConfig(Value)


class ParamsManager:
    def __init__(self,
        ConfigPath: str,
    ):
        self.ConfigPath = ConfigPath
        self.Config = QFunc.ManageConfig(ConfigPath)

        self.RegistratedWidgets = {}

    def Registrate(self, Widget: QWidget, value: tuple):
        self.RegistratedWidgets[Widget] = value

    def SetParam(self,
        Widget: QWidget,
        Section: str = ...,
        Option: str = ...,
        DefaultValue = None,
        Times: Union[int, float] = 1,
        SetPlaceholderText: bool = False,
        PlaceholderText: Optional[str] = None,
        Registrate: bool = True
    ):
        Value = self.Config.GetValue(Section, Option, str(DefaultValue))
        Function_SetWidgetValue(Widget, self.Config, Section, Option, Value, Times, SetPlaceholderText, PlaceholderText)
        self.Registrate(Widget, (Section, Option, DefaultValue, Times, SetPlaceholderText, PlaceholderText)) if Registrate else None

    def ResetParam(self, Widget: QWidget):
        value = self.RegistratedWidgets[Widget]
        Function_SetWidgetValue(Widget, self.Config, *value)

    def ClearSettings(self):
        with open(self.ConfigPath, 'w'):
            pass
        self.Config = QFunc.ManageConfig(self.ConfigPath)

    def ResetSettings(self):
        self.ClearSettings()
        for Widget in list(self.RegistratedWidgets.keys()):
            self.ResetParam(Widget)

    def ImportSettings(self, ReadPath: str):
        ConfigParser = QFunc.ManageConfig(ReadPath).Parser()
        with open(self.ConfigPath, 'w', encoding = 'utf-8') as Config:
            ConfigParser.write(Config)
        for Widget, value in list(self.RegistratedWidgets.items()):
            self.SetParam(Widget, *value)

    def ExportSettings(self, SavePath: str):
        with open(SavePath, 'w', encoding = 'utf-8') as Config:
            self.Config.Parser().write(Config)

##############################################################################################################################