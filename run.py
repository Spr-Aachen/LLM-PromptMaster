# -*- coding: utf-8 -*-

import argparse
import ctypes
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

##############################################################################################################################

# 路径一律基于启动器自身位置, 保证从任意目录启动结果一致
rootDir = Path(__file__).resolve().parent

serverEntry = rootDir.joinpath("server", "main.py")
clientEntry = rootDir.joinpath("client", "main.py")

# 运行时数据根目录：data/{server,client}, 单实例锁也在根下
dataDirName = "data"
defaultDataDir = rootDir.joinpath(dataDirName)

# 单实例锁, 记录启动器 pid 与服务端端口
lockFileName = "launcher.lock"

# 未指定 --port 时的探测范围
defaultPortRange = (8000, 8080)

# 等待服务端就绪 / 等待服务端退出 / 必要时强杀的时限 (秒)
healthTimeout = 60.0
healthInterval = 0.2
shutdownTimeout = 10.0
terminateTimeout = 3.0

# 本地请求不走系统代理
urlOpener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

##############################################################################################################################

def parseArguments(argv: Optional[list] = None) -> argparse.Namespace:
    """
    解析启动参数
    """
    parser = argparse.ArgumentParser(description = "LLM PromptMaster 启动器")
    parser.add_argument("--host", help = "服务端监听地址", type = str, default = "127.0.0.1")
    parser.add_argument("--port", help = f"服务端端口 (缺省时在 {defaultPortRange[0]}-{defaultPortRange[1]} 中探测)", type = int, default = None)
    parser.add_argument("--client", help = "客户端模式: gui 启动图形界面, none 只运行服务端", type = str, default = "gui", choices = ("gui", "none"))
    parser.add_argument("--data-dir", dest = "dataDir", help = f"运行时数据根目录, 其下分 server/ 与 client/ (缺省为 {dataDirName}/)", type = str, default = None)
    parser.add_argument("--log-level", dest = "logLevel", help = "服务端日志级别", type = str, default = None)
    return parser.parse_args(argv)


def log(message: str, *params):
    """
    启动器日志: 带时间戳输出到控制台
    """
    text = message % params if params else message
    print(f"[{time.strftime('%H:%M:%S')}] [launcher] {text}", flush = True)

##############################################################################################################################

def isPortFree(host: str, port: int) -> bool:
    """
    通过临时绑定判断端口是否可用
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def resolvePort(host: str, explicitPort: Optional[int]) -> Optional[int]:
    """
    显式端口被占用则报错, 否则在默认范围内取第一个可用端口
    """
    if explicitPort is not None:
        if not isPortFree(host, explicitPort):
            log("端口 %s 已被占用, 请更换 --port 或先释放该端口", explicitPort)
            return None
        return explicitPort
    for port in range(defaultPortRange[0], defaultPortRange[1] + 1):
        if isPortFree(host, port):
            return port
    log("端口 %s-%s 均被占用, 请使用 --port 指定", *defaultPortRange)
    return None

##############################################################################################################################

def readLock(lockFile: Path) -> Optional[dict]:
    """
    读取锁文件, 内容损坏时视为无效
    """
    try:
        lockInfo = json.loads(lockFile.read_text(encoding = "utf-8"))
    except (OSError, ValueError):
        return None
    return lockInfo if isinstance(lockInfo, dict) else None


def writeLock(lockFile: Path, lockInfo: dict):
    """
    写入锁文件 (记录启动器 pid 与实际端口)
    """
    lockFile.parent.mkdir(parents = True, exist_ok = True)
    lockFile.write_text(json.dumps(lockInfo, ensure_ascii = False, indent = 2), encoding = "utf-8")


def releaseLock(lockFile: Path):
    """
    仅删除自己写入的锁文件
    """
    lockInfo = readLock(lockFile)
    if lockInfo is not None and lockInfo.get("pid") not in (None, os.getpid()):
        return
    try:
        lockFile.unlink()
    except OSError:
        pass


def isProcessAlive(pid: Optional[int]) -> bool:
    """
    判断进程是否存活 (Windows 下不能用 os.kill(pid, 0), 它会直接结束目标进程)
    """
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
    processQueryLimitedInformation = 0x1000
    stillActive = 259
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(processQueryLimitedInformation, False, pid)
    if not handle:
        return False
    try:
        exitCode = ctypes.c_ulong()
        return bool(kernel32.GetExitCodeProcess(handle, ctypes.byref(exitCode))) and exitCode.value == stillActive
    finally:
        kernel32.CloseHandle(handle)

##############################################################################################################################

def requestHealth(host: str, port: int, timeout: float = 1.0) -> Optional[dict]:
    """
    请求 /health, 失败返回 None
    """
    try:
        with urlOpener.open(f"http://{host}:{port}/health", timeout = timeout) as response:
            if response.status != 200:
                return None
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError):
        return None


def waitForHealth(host: str, port: int, process: subprocess.Popen) -> Optional[dict]:
    """
    轮询 /health 直到就绪、子进程退出或超时
    """
    deadline = time.monotonic() + healthTimeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            log("服务端提前退出 (code=%s)", process.returncode)
            return None
        healthInfo = requestHealth(host, port)
        if healthInfo is not None:
            return healthInfo
        time.sleep(healthInterval)
    return None


def requestShutdown(host: str, port: int, timeout: float = 2.0) -> bool:
    """
    请求服务端优雅退出
    """
    request = urllib.request.Request(f"http://{host}:{port}/shutdown", method = "POST", data = b"")
    try:
        with urlOpener.open(request, timeout = timeout) as response:
            return response.status == 200
    except (urllib.error.URLError, OSError, ValueError):
        return False

##############################################################################################################################

def startProcess(name: str, command: list) -> Optional[subprocess.Popen]:
    """
    以参数列表启动子进程 (shell=False)
    """
    try:
        process = subprocess.Popen(command, cwd = str(rootDir), shell = False)
    except OSError as e:
        log("%s启动失败: %s", name, e)
        return None
    log("%s已启动 (pid=%s)", name, process.pid)
    return process


def stopServer(process: Optional[subprocess.Popen], host: str, port: int):
    """
    先请求 /shutdown, 超时后退化为 terminate / kill
    """
    if process is None or process.poll() is not None:
        return
    if requestShutdown(host, port):
        log("已通知服务端退出, 等待最多 %.0fs", shutdownTimeout)
    else:
        log("关闭请求失败, 等待 %.0fs 后强制结束服务端", shutdownTimeout)
    deadline = time.monotonic() + shutdownTimeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            log("服务端已退出 (code=%s)", process.returncode)
            return
        time.sleep(healthInterval)
    log("服务端未在 %.0fs 内退出, 发送终止信号", shutdownTimeout)
    process.terminate()
    try:
        process.wait(timeout = terminateTimeout)
    except subprocess.TimeoutExpired:
        log("服务端仍未退出, 强制结束")
        process.kill()
        process.wait()

##############################################################################################################################

def resolveDataDir(explicit: Optional[str] = None) -> Path:
    """
    数据根目录: 显式参数优先, 否则项目根目录下的 data/
    """
    return Path(explicit).expanduser().resolve() if explicit else defaultDataDir


def buildServerCommand(host: str, port: int, dataDir: Path, argument: argparse.Namespace) -> list:
    """
    服务端命令: 使用当前解释器与参数列表, 并显式指定数据目录
    """
    command = [sys.executable, "-u", str(serverEntry), "--host", host, "--port", str(port), "--work-dir", str(dataDir.joinpath("server"))]
    if argument.logLevel:
        command += ["--log-level", argument.logLevel]
    return command


def buildClientCommand(host: str, port: int, dataDir: Path) -> list:
    """
    客户端命令: 显式传入实际端口与配置目录
    """
    return [sys.executable, "-u", str(clientEntry), "--host", host, "--port", str(port), "--profileDir", str(dataDir.joinpath("client"))]

##############################################################################################################################

def run(argument: argparse.Namespace) -> int:
    """
    启动流程: 单实例检查 → 探测端口 → 起服务端 → 等 /health → 起客户端 → 退出后关停服务端
    """
    host = argument.host
    dataDir = resolveDataDir(argument.dataDir)
    lockFile = dataDir.joinpath(lockFileName)

    log("项目根目录: %s", rootDir.as_posix())
    log("数据目录: %s", dataDir.as_posix())

    if not serverEntry.is_file():
        log("服务端入口不存在: %s", serverEntry.as_posix())
        return 1
    if argument.client != "none" and not clientEntry.is_file():
        log("客户端入口不存在: %s", clientEntry.as_posix())
        return 1

    # 单实例检查: 锁记录的服务端仍健康则提示并退出
    lockInfo = readLock(lockFile)
    if lockInfo is not None:
        lockHost = lockInfo.get("host") or host
        lockPort = lockInfo.get("port")
        healthInfo = requestHealth(lockHost, lockPort) if isinstance(lockPort, int) else None
        if healthInfo is not None:
            log("检测到已运行的实例 (pid=%s, 端口=%s), 请先关闭旧实例", healthInfo.get("pid"), lockPort)
            return 0
        if isProcessAlive(lockInfo.get("pid")):
            log("另一个启动器正在启动中 (pid=%s), 请稍后重试; 如确认无实例运行可删除 %s", lockInfo.get("pid"), lockFile.as_posix())
            return 1
        log("清理失效的锁文件: %s", lockFile.as_posix())
        releaseLock(lockFile)

    port = resolvePort(host, argument.port)
    if port is None:
        return 2
    log("使用端口: %s", port)

    serverProcess = None
    try:
        writeLock(lockFile, {
            "pid": os.getpid(),
            "host": host,
            "port": port,
            "startedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        serverProcess = startProcess("服务端", buildServerCommand(host, port, dataDir, argument))
        if serverProcess is None:
            return 1
        log("等待服务端就绪, 超时 %.0fs", healthTimeout)
        healthInfo = waitForHealth(host, port, serverProcess)
        if healthInfo is None:
            log("服务端未就绪, 放弃启动客户端")
            return 1
        log("服务端就绪: http://%s:%s 版本=%s 工作目录=%s", host, port, healthInfo.get("version"), healthInfo.get("workDir"))

        if argument.client == "none":
            log("仅运行服务端, 按 Ctrl+C 退出")
            serverProcess.wait()
            return serverProcess.returncode or 0

        clientProcess = startProcess("客户端", buildClientCommand(host, port, dataDir))
        if clientProcess is None:
            return 1
        exitCode = clientProcess.wait()
        log("客户端已退出 (code=%s)", exitCode)
        return exitCode
    finally:
        stopServer(serverProcess, host, port)
        releaseLock(lockFile)

##############################################################################################################################

if __name__ == "__main__":
    try:
        exitCode = run(parseArguments())
    except KeyboardInterrupt:
        log("收到中断, 正在退出")
        exitCode = 130
    sys.exit(exitCode)

##############################################################################################################################