# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
from typing import Optional
from subprocess import Popen

##############################################################################################################################

# Get current directory
CurrentDir = sys.path[0]


IsCompiled = False


def run(
    env: str = 'uat',
    port: Optional[int] = None,
):
    if not IsCompiled:
        BackendDir = Path(f'{CurrentDir}{os.sep}backend').as_posix()
        backendFile = Path(f'{BackendDir}{os.sep}main.py').as_posix()
        Popen(
            f'cd "{BackendDir}" & python "{backendFile}" -e {env} -p {port}',
            shell = True
        )
        FrontendDir = Path(f'{CurrentDir}{os.sep}frontend').as_posix()
        FrontendFile = Path(f'{FrontendDir}{os.sep}main.py').as_posix()
        Popen(
            f'cd "{FrontendDir}" & python "{FrontendFile}"',
            shell = True
        )
    else:
        ''''''

##############################################################################################################################

if __name__ == "__main__":
    run(
        env = 'prod',
        port = 8080,
    )

##############################################################################################################################