from pathlib import Path
from QEasyWidgets.Utils import *

##############################################################################################################################

# Check whether python file is compiled
_, IsFileCompiled = GetFileInfo()

# Get current directory
CurrentDir = GetBaseDir(__file__ if IsFileCompiled == False else sys.executable)

# Set directory to store client config
ConfigDir = NormPath(Path(CurrentDir).joinpath('Config'))

# Set path of client config
ConfigPath = NormPath(Path(ConfigDir).joinpath('Config.ini'))

##############################################################################################################################