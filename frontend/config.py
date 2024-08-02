from pathlib import Path
from QEasyWidgets.Utils import *

##############################################################################################################################

# Check whether python file is compiled
_, IsFileCompiled = GetFileInfo()

# Get current directory
CurrentDir = GetBaseDir(__file__ if IsFileCompiled == False else sys.executable)

# Set root directory
RootDir = Path(CurrentDir).parent.as_posix()

# Set directory to store conversations
ConversationDir = NormPath(Path(RootDir).joinpath('Conversations'))

# Set directory to store questions
QuestionDir = NormPath(Path(RootDir).joinpath('Questions'))

# Set directory to store client config
ConfigDir = NormPath(Path(RootDir).joinpath('Config'))
# Set path of client config
ConfigPath = NormPath(Path(RootDir).joinpath('Config.ini'))

##############################################################################################################################