from typing import Union, Optional
from PySide6.QtCore import Qt, QObject, Signal, Slot, QThread
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc
from QEasyWidgets.Windows import *
from QEasyWidgets.Components import *

from components import *
from windows import *

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
    checkBox: QCheckBox,
    checkedText: Optional[str] = None,
    checkedEvents: list = [],
    uncheckedText: Optional[str] = None,
    uncheckedEvents: list = [],
    takeEffect: bool = False
):
    '''
    Function to configure checkbox
    '''
    if checkedText is not None:
        checkedEvents.append(lambda: checkBox.setText(checkedText))
    if uncheckedText is not None:
        uncheckedEvents.append(lambda: checkBox.setText(uncheckedText))

    checkBox.toggled.connect(
        lambda IsChecked: QFunc.runEvents(checkedEvents if IsChecked else uncheckedEvents)
    )

    QFunc.runEvents(checkedEvents) if takeEffect and checkBox.isChecked() else None
    QFunc.runEvents(uncheckedEvents) if takeEffect and not checkBox.isChecked() else None

##############################################################################################################################

def Function_AnimateStackedWidget(
    stackedWidget: QStackedWidget,
    target: Union[int, QWidget] = 0,
    duration: int = 99
):
    '''
    Function to animate stackedwidget
    '''
    OriginalWidget = stackedWidget.currentWidget()
    OriginalGeometry = OriginalWidget.geometry()

    if isinstance(target, int):
        TargetIndex = target
    if isinstance(target, QWidget):
        TargetIndex = stackedWidget.indexOf(target)

    WidgetAnimation = QFunc.setWidgetPosAnimation(OriginalWidget, duration)
    WidgetAnimation.finished.connect(
        lambda: stackedWidget.setCurrentIndex(TargetIndex),
        type = Qt.QueuedConnection
    )
    WidgetAnimation.finished.connect(
        lambda: OriginalWidget.setGeometry(OriginalGeometry),
        type = Qt.QueuedConnection
    )
    WidgetAnimation.start() if stackedWidget.currentIndex() != TargetIndex else None

##############################################################################################################################

def Function_SetWidgetValue(
    widget: QWidget,
    config: QFunc.configManager,
    section: str = ...,
    option: str = ...,
    value = ...,
    times: Union[int, float] = 1,
    setPlaceholderText: bool = False,
    placeholderText: Optional[str] = None
):
    if isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit)):
        QFunc.setText(widget, value, setPlaceholderText = setPlaceholderText, placeholderText = placeholderText)
        def EditConfig(value):
            config.editConfig(section, option, str(value))
        if config is not None:
            widget.textChanged.connect(lambda: EditConfig(widget.text() if isinstance(widget, (QLineEdit)) else widget.toPlainText()))
            EditConfig(value)

    if isinstance(widget, (QComboBox)):
        itemTexts = []
        for index in range(widget.count()):
            itemTexts.append(widget.itemText(index))
        widget.setCurrentText(str(value)) if str(value) in itemTexts else None
        def EditConfig(value):
            config.editConfig(section, option, str(value))
        if config is not None:
            widget.currentTextChanged.connect(EditConfig)
            EditConfig(value) if str(value) in itemTexts else None

    if isinstance(widget, (QSpinBox, QSlider)):
        widget.setValue(int(eval(str(value)) * times))
        def EditConfig(value):
            config.editConfig(section, option, str(eval(str(value)) / times))
        if config is not None:
            widget.valueChanged.connect(EditConfig)
            EditConfig(value)

    if isinstance(widget, (QDoubleSpinBox, SliderBase)):
        widget.setValue(float(eval(str(value)) * times))
        def EditConfig(value):
            config.editConfig(section, option, str(eval(str(value)) / times))
        if config is not None:
            widget.valueChanged.connect(EditConfig)
            EditConfig(value)

    if isinstance(widget, (QCheckBox, QRadioButton)):
        widget.setChecked(eval(str(value)))
        def EditConfig(value):
            config.editConfig(section, option, str(value))
        if config is not None:
            widget.toggled.connect(EditConfig)
            EditConfig(value)


class ParamsManager:
    def __init__(self,
        configPath: str,
    ):
        self.configPath = configPath
        self.config = QFunc.configManager(configPath)

        self.RegistratedWidgets = {}

    def registrate(self, widget: QWidget, value: tuple):
        self.RegistratedWidgets[widget] = value

    def SetParam(self,
        widget: QWidget,
        section: str = ...,
        option: str = ...,
        defaultValue = None,
        times: Union[int, float] = 1,
        setPlaceholderText: bool = False,
        placeholderText: Optional[str] = None,
        registrate: bool = True
    ):
        value = self.config.getValue(section, option, str(defaultValue))
        Function_SetWidgetValue(widget, self.config, section, option, value, times, setPlaceholderText, placeholderText)
        self.registrate(widget, (section, option, defaultValue, times, setPlaceholderText, placeholderText)) if registrate else None

    def ResetParam(self, widget: QWidget):
        value = self.RegistratedWidgets[widget]
        Function_SetWidgetValue(widget, self.config, *value)

    def ClearSettings(self):
        with open(self.configPath, 'w'):
            pass
        self.config = QFunc.configManager(self.configPath)

    def ResetSettings(self):
        self.ClearSettings()
        for widget in list(self.RegistratedWidgets.keys()):
            self.ResetParam(widget)

    def ImportSettings(self, readPath: str):
        configParser = QFunc.configManager(readPath).parser()
        with open(self.configPath, 'w', encoding = 'utf-8') as config:
            configParser.write(config)
        for widget, value in list(self.RegistratedWidgets.items()):
            self.SetParam(widget, *value)

    def ExportSettings(self, savePath: str):
        with open(savePath, 'w', encoding = 'utf-8') as config:
            self.config.parser().write(config)

##############################################################################################################################