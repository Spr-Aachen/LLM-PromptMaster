# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Optional
from subprocess import Popen
from QEasyWidgets import QFunctions as QFunc

##############################################################################################################################

# Check whether python file is compiled
_, IsFileCompiled = QFunc.GetFileInfo()

# Get current directory
CurrentDir = QFunc.GetBaseDir(__file__ if IsFileCompiled == False else sys.executable)

# Set profile directory
ProfileDir = Path(CurrentDir).joinpath('Profile').as_posix()

# Set directory to store prompts
PromptDir = Path(ProfileDir).joinpath('Prompts').as_posix()

# Set directory to store conversations
ConversationDir = Path(ProfileDir).joinpath('Conversations').as_posix()

# Set directory to store questions
QuestionDir = Path(ProfileDir).joinpath('Questions').as_posix()

# Set directory to store client config
ConfigDir = Path(ProfileDir).joinpath('Config').as_posix()

##############################################################################################################################

def run(
    env: str = 'uat',
    port: Optional[int] = None,
):
    # 后台启动
    BackendDir = Path(f'{CurrentDir}{os.sep}backend').as_posix()
    backendFile = Path(f'{BackendDir}{os.sep}main.py').as_posix()
    Popen(
        f'cd "{BackendDir}" & python "{backendFile}" -e {env} -p {port}',
        shell = True
    )

    # 前台启动
    FrontendDir = Path(f'{CurrentDir}{os.sep}frontend').as_posix()
    FrontendFile = Path(f'{FrontendDir}{os.sep}main.py').as_posix()
    Popen(
        f'cd "{FrontendDir}" & python "{FrontendFile}" --promptdir "{PromptDir}" --conversationdir "{ConversationDir}" --questiondir "{QuestionDir}" --configdir "{ConfigDir}"',
        shell = True
    )

##############################################################################################################################

if __name__ == "__main__":
    run(
        env = 'prod',
        port = 8080,
    )

##############################################################################################################################