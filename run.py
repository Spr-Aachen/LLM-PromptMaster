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
    env: str = 'uat',
    port: Optional[int] = None,
    profileDir: Optional[str] = None
):
    if not IsCompiled:
        backendDir = Path(f'{CurrentDir}{os.sep}backend').as_posix()
        backendFile = Path(f'{backendDir}{os.sep}main.py').as_posix()
        Popen(
            f'cd "{backendDir}" & python "{backendFile}" -e "{env}" -p {port}',
            shell = True
        )
        frontendDir = Path(f'{CurrentDir}{os.sep}frontend').as_posix()
        frontendFile = Path(f'{frontendDir}{os.sep}main.py').as_posix()
        Popen(
            f'cd "{frontendDir}" & python "{frontendFile}" --profiledir "{profileDir}"',
            shell = True
        )
    else:
        ''''''

##############################################################################################################################

if __name__ == "__main__":
    run(
        env = 'prod',
        port = 8080,
        profileDir = Path(CurrentDir).joinpath('User Profile').as_posix()
    )

##############################################################################################################################