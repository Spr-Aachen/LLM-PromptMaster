import sys
import PyEasyUtils as EasyUtils
from pathlib import Path

##############################################################################################################################

# Check whether python file is compiled
_, isFileCompiled = EasyUtils.getFileInfo()

# Get current directory
currentDir = EasyUtils.getBaseDir(__file__ if isFileCompiled == False else sys.executable)

##############################################################################################################################