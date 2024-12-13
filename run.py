# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Optional
from subprocess import Popen

##############################################################################################################################

# Get current directory
CurrentDir = Path(sys.argv[0]).parent.as_posix()


IsCompiled = False


def run(
    host: str = 'localhost',
    port: Optional[int] = None,
    profileDir: Optional[str] = None
):
    resourceDir = Path(sys._MEIPASS).as_posix() if getattr(sys, 'frozen', None) else CurrentDir
    backendDir = Path(f'{resourceDir}{os.sep}backend').as_posix()
    backendFile = Path(f'{backendDir}{os.sep}main.py').as_posix()
    backendCMD = f'python "{backendFile}" --host "{host}" --port {port}'
    Popen(backendCMD)
    frontendDir = Path(f'{resourceDir}{os.sep}frontend').as_posix()
    frontendFile = Path(f'{frontendDir}{os.sep}main.py').as_posix()
    frontendCMD = f'python "{frontendFile}" --host "{host}" --port {port} --profiledir "{profileDir}"'
    Popen(frontendCMD)

##############################################################################################################################

if __name__ == "__main__":
    run(
        host = 'localhost',
        port = 80,
        profileDir = Path(CurrentDir).joinpath('User Profile').as_posix()
    )

##############################################################################################################################