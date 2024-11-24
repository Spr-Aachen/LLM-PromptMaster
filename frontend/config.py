import sys
from pathlib import Path
from QEasyWidgets import QFunctions as QFunc

##############################################################################################################################

# Check whether python file is compiled
_, isFileCompiled = QFunc.getFileInfo()

# Get current directory
currentDir = QFunc.getBaseDir(__file__ if isFileCompiled == False else sys.executable)

##############################################################################################################################