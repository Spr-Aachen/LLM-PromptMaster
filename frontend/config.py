import sys
from pathlib import Path
from QEasyWidgets import QFunctions as QFunc

##############################################################################################################################

# Check whether python file is compiled
_, IsFileCompiled = QFunc.GetFileInfo()

# Get current directory
CurrentDir = QFunc.GetBaseDir(__file__ if IsFileCompiled == False else sys.executable)

# Set root directory
RootDir = Path(CurrentDir).parent.as_posix()

# Set directory to store prompts
PromptDir = QFunc.NormPath(Path(RootDir).joinpath('Prompts'))

# Set directory to store conversations
ConversationDir = QFunc.NormPath(Path(RootDir).joinpath('Conversations'))

# Set directory to store questions
QuestionDir = QFunc.NormPath(Path(RootDir).joinpath('Questions'))

# Set directory to store client config
ConfigDir = QFunc.NormPath(Path(RootDir).joinpath('Config'))
# Set path of client config
ConfigPath = QFunc.NormPath(Path(RootDir).joinpath('Config.ini'))

##############################################################################################################################