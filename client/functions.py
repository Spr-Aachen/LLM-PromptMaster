import PyEasyUtils as EasyUtils
from typing import Union, Optional
from PySide6.QtCore import Qt, QObject, Signal, QThreadPool
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from QEasyWidgets import QFunctions as QFunc, QWorker
from QEasyWidgets.Windows import *
from QEasyWidgets.Components import *

from components import *

##############################################################################################################################

# Where to store custom signals
class CustomSignals_Functions(QObject):
    '''
    Set up signals for functions
    '''
    executeTask = Signal(tuple)
    taskStatus = Signal(str, str)

    forceQuit = Signal()


functionSignals = CustomSignals_Functions()

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
        lambda IsChecked: EasyUtils.runEvents(checkedEvents if IsChecked else uncheckedEvents)
    )

    EasyUtils.runEvents(checkedEvents) if takeEffect and checkBox.isChecked() else None
    EasyUtils.runEvents(uncheckedEvents) if takeEffect and not checkBox.isChecked() else None

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
    WidgetAnimation.start()


def Function_AnimateFrame(
    frame: QWidget,
    minWidth: Optional[int] = None,
    maxWidth: Optional[int] = None,
    minHeight: Optional[int] = None,
    maxHeight: Optional[int] = None,
    duration: int = 210,
    mode: str = "Toggle",
):
    '''
    Function to animate frame
    '''
    def ExtendFrame():
        QFunc.setWidgetSizeAnimation(frame, maxWidth, None, duration).start() if maxWidth not in (None, frame.width()) else None
        QFunc.setWidgetSizeAnimation(frame, None, maxHeight, duration).start() if maxHeight not in (None, frame.height()) else None

    def ReduceFrame():
        QFunc.setWidgetSizeAnimation(frame, minWidth, None, duration).start() if minWidth not in (None, frame.width()) else None
        QFunc.setWidgetSizeAnimation(frame, None, minHeight, duration).start() if minHeight not in (None, frame.height()) else None

    if mode == "Extend":
        ExtendFrame()
    if mode == "Reduce":
        ReduceFrame()
    if mode == "Toggle":
        ExtendFrame() if frame.width() == minWidth or frame.height() == minHeight else ReduceFrame()

##############################################################################################################################

def Function_SetWidgetValue(
    widget: QWidget,
    config: EasyUtils.configManager,
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

    if isinstance(widget, (Table_APIKeys)):
        widget.setValue(eval(str(value)))
        def EditConfig(value):
            config.editConfig(section, option, str(value))
        if config is not None:
            widget.valueChanged.connect(EditConfig)
            EditConfig(value)


class ParamsManager:
    def __init__(self,
        configPath: str,
    ):
        self.configPath = configPath
        self.config = EasyUtils.configManager(configPath)

        self.RegistratedWidgets = {}

    def registrate(self, widget: QWidget, value: tuple):
        self.RegistratedWidgets[widget] = value

    def setParam(self,
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

    def resetParam(self, widget: QWidget):
        value = self.RegistratedWidgets[widget]
        Function_SetWidgetValue(widget, self.config, *value)

    def clearSettings(self):
        with open(self.configPath, 'w'):
            pass
        self.config = EasyUtils.configManager(self.configPath)

    def resetSettings(self):
        self.clearSettings()
        for widget in list(self.RegistratedWidgets.keys()):
            self.resetParam(widget)

    def importSettings(self, readPath: str):
        configParser = EasyUtils.configManager(readPath).parser()
        with open(self.configPath, 'w', encoding = 'utf-8') as config:
            configParser.write(config)
        for widget, value in list(self.RegistratedWidgets.items()):
            self.setParam(widget, *value)

    def exportSettings(self, savePath: str):
        with open(savePath, 'w', encoding = 'utf-8') as config:
            self.config.parser().write(config)

##############################################################################################################################

def Function_GetParam(
    ui: QObject
):
    '''
    Function to get the param of ui
    '''
    if isinstance(ui, (QLineEdit, QTextEdit, QPlainTextEdit)):
        return QFunc.getText(ui)
    if isinstance(ui, QComboBox):
        return ui.currentText()
    if isinstance(ui, (QAbstractSpinBox, QSlider)):
        return ui.value()
    if isinstance(ui, (QCheckBox, QRadioButton)):
        return ui.isChecked()


def Function_SetParam(
    ui: QObject,
    param: Optional[str]
):
    '''
    Function to set the param of ui
    '''
    if isinstance(ui, (QLineEdit, QTextEdit)):
        ui.setText(param)
    if isinstance(ui, QPlainTextEdit):
        ui.setPlainText(param)
    if isinstance(ui, QComboBox):
        ui.setCurrentText(param)
    if isinstance(ui, (QAbstractSpinBox, QSlider)):
        ui.setValue(param)
    if isinstance(ui, (QCheckBox, QRadioButton)):
        ui.setChecked(param)


def Function_ParamsChecker(
    paramTarget: object,
    emptyAllowed: bool
):
    '''
    Function to return handled param
    '''
    param = Function_GetParam(paramTarget) if isinstance(paramTarget, QWidget) else paramTarget
    if isinstance(param, str):
        if param.strip() == "None" or param.strip() == "":
            if emptyAllowed:
                param = None
            else:
                MessageBoxBase.pop(
                    messageType = QMessageBox.Warning,
                    windowTitle = "Warning",
                    text = "Empty param detected!\n检测到参数空缺！"
                )
                return "Abort"
        else:
            '''
            if "，" in param or "," in param:
                param = re.split(
                    pattern = '[，,]',
                    string = param,
                    maxsplit = 0
                )
            '''
    if isinstance(param, dict):
        if "None" in list(param.keys()&param.values()) or "" in list(param.keys()&param.values()):
            if emptyAllowed:
                param = None
            else:
                MessageBoxBase.pop(
                    messageType = QMessageBox.Warning,
                    windowTitle = "Warning",
                    text = "Empty param detected!\n检测到参数空缺！"
                )
                return "Abort"
        else:
            pass

    return param

##############################################################################################################################

class TaskStatus:
    Started = 'Started'
    Finished = 'Finished'
    Failed = 'Failed'
    Succeeded = 'Succeeded'


class WorkerManager(QWorker.WorkerManager):
    def __init__(self,
        executeMethod: object = ...,
        executeParams: Optional[dict] = None,
        terminateMethod: Optional[object] = None,
        autoDelete: bool = True,
        threadPool: Optional[QThreadPool] = None,
    ):
        super().__init__(executeMethod, terminateMethod, autoDelete, threadPool)

        self.executeMethodName = executeMethod.__qualname__
        self.executeParams = executeParams

        self.signals = QWorker.WorkerSignals()
        self.worker.signals.started.connect(self.signals.started.emit)
        self.worker.signals.error.connect(self.signals.error.emit)
        self.worker.signals.result.connect(self.signals.result.emit)
        self.worker.signals.finished.connect(self.signals.finished.emit)
        self.signals.started.connect(
            lambda: functionSignals.taskStatus.emit(self.executeMethodName, TaskStatus.Started)
        )
        self.signals.error.connect(
            lambda: functionSignals.taskStatus.emit(self.executeMethodName, TaskStatus.Failed)
        )
        self.signals.finished.connect(
            lambda: functionSignals.taskStatus.emit(self.executeMethodName, TaskStatus.Finished)
        )

        functionSignals.forceQuit.connect(self.terminate)

    def _validateParams(self, unvalidatedParams):
        validatedParams = []
        if unvalidatedParams is not None:
            unvalidatedParams = [(unvalidatedParam, unvalidatedParams[unvalidatedParam] if isinstance(unvalidatedParams, dict) else True) for unvalidatedParam in EasyUtils.toIterable(unvalidatedParams)]
            for paramTarget, emptyAllowed in unvalidatedParams:
                param = Function_ParamsChecker(paramTarget, emptyAllowed)
                if param == "Abort":
                    return print("Aborted.")
                else:
                    pass #print("Continued.\n")
                validatedParams.append(param)
        return validatedParams

    def execute(self):
        super().execute(*self._validateParams(self.executeParams))

    def terminate(self):
        super().terminate()
        functionSignals.taskStatus.emit(self.executeMethodName, TaskStatus.Failed)


def Function_SetMethodExecutor(
    executeMethod: object = ...,
    executeParams: Optional[dict] = None,
    executeButton: Optional[QAbstractButton] = None,
    terminateMethod: Optional[object] = None,
    terminateButton: Optional[QAbstractButton] = None,
    finishedEvents: Optional[dict] = None,
    autoDelete: bool = True,
    threadPool: Optional[QThreadPool] = None,
    parentWindow: Optional[QWidget] = None,
):
    '''
    '''
    workerManager = WorkerManager(executeMethod, executeParams, terminateMethod, autoDelete, threadPool)

    isErrorOccurred = False
    def _setErrorOccuredFlag():
        global isErrorOccurred
        isErrorOccurred = True

    workerManager.signals.started.connect(
        lambda: (
            Function_AnimateStackedWidget(QFunc.findParent(executeButton, QStackedWidget), target = 1) if terminateButton else None,
        )
    )
    workerManager.signals.error.connect(
        lambda err: (
            _setErrorOccuredFlag(),
            MessageBoxBase.pop(parentWindow, QMessageBox.Warning, "Failure", "发生异常", err),
            EasyUtils.runEvents([event for event, status in finishedEvents.items() if status == TaskStatus.Failed]) if finishedEvents is not None else None,
        )
    )
    workerManager.signals.finished.connect(
        lambda: (
            Function_AnimateStackedWidget(QFunc.findParent(executeButton, QStackedWidget), target = 0) if terminateButton else None,
            EasyUtils.runEvents([event for event, status in finishedEvents.items() if (not isErrorOccurred and status == TaskStatus.Succeeded) or TaskStatus.Finished]) if finishedEvents is not None else None,
        )
    )

    # Execution
    if executeButton is not None:
        executeButton.clicked.connect(workerManager.execute)
    else:
        tempButton = QPushButton(parentWindow)
        tempButton.clicked.connect(workerManager.execute)
        tempButton.setVisible(False)
        tempButton.click()
        workerManager.signals.finished.connect(tempButton.deleteLater)

    # Termination
    if terminateButton is not None:
        terminateButton.clicked.connect(
            lambda: MessageBoxBase.pop(parentWindow,
                messageType = QMessageBox.Question,
                windowTitle = "Ask",
                text = "当前任务仍在执行中，是否确认终止？",
                buttons = QMessageBox.Yes|QMessageBox.No,
                buttonEvents = {QMessageBox.Yes: workerManager.terminate}
            )
        )
    else:
        pass

##############################################################################################################################