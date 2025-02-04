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
    serverDir = Path(f'{resourceDir}{os.sep}server').as_posix()
    serverFile = Path(f'{serverDir}{os.sep}main.py').as_posix()
    serverCMD = f'python "{serverFile}" --host "{host}" --port {port}'
    Popen(serverCMD)
    clientDir = Path(f'{resourceDir}{os.sep}client').as_posix()
    clientFile = Path(f'{clientDir}{os.sep}main.py').as_posix()
    clientCMD = f'python "{clientFile}" --host "{host}" --port {port} --profiledir "{profileDir}"'
    Popen(clientCMD)

##############################################################################################################################

if __name__ == "__main__":
    run(
        host = 'localhost',
        port = 80,
        profileDir = Path(CurrentDir).joinpath('User Profile').as_posix()
    )

##############################################################################################################################