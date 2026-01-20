#!/usr/bin/env python3
"""
性能监控脚本 - 使用 py-spy 监控 FastAPI 应用性能

使用方法:
    # 方式1: 直接指定进程 PID
    python scripts/spy/monitor.py --pid 12345

    # 方式2: 等待应用启动并获取 PID
    python scripts/spy/monitor.py --wait --timeout 30

    # 方式3: 启动应用并自动监控
    python scripts/spy/monitor.py --start --port 8000

    # 方式4: 持续记录性能数据
    python scripts/spy/monitor.py --record --duration 60 --output profile.svg

    # 方式5: 列出所有 Uvicorn 进程
    python scripts/spy/monitor.py --list
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import psutil
except ImportError:
    print("请安装 psutil: pip install psutil")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).parent.parent.parent
SPY_DATA_DIR = PROJECT_ROOT / "scripts" / "spy" / "data"
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
if sys.platform != "win32":
    VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"

global_processes = []


def find_uvicorn_processes() -> list[dict]:
    """查找所有 Uvicorn 工作进程"""
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = proc.info.get("cmdline", [])
            if cmdline and "uvicorn" in " ".join(cmdline):
                processes.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "cmdline": " ".join(cmdline),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes


def find_process_by_port(port: int) -> Optional[int]:
    """根据端口查找进程 PID"""
    for conn in psutil.net_connections():
        if conn.status == "LISTEN" and conn.laddr.port == port:
            return conn.pid
    return None


def wait_for_app_start(port: int, timeout: int = 30) -> Optional[int]:
    """等待应用启动并返回 PID"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        pid = find_process_by_port(port)
        if pid:
            return pid
        time.sleep(0.5)
    return None


def kill_process_tree(pid: int):
    """终止进程及其所有子进程"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        gone, alive = psutil.wait_procs(children, timeout=3)
        for p in alive:
            try:
                p.kill()
            except psutil.NoSuchProcess:
                pass
        parent.terminate()
        parent.wait(timeout=3)
    except psutil.NoSuchProcess:
        pass
    except Exception:
        try:
            if sys.platform == "win32":
                os.system(f"taskkill /F /PID {pid} >nul 2>&1")
            else:
                os.kill(pid, signal.SIGTERM)
        except (OSError, ProcessLookupError):
            pass


def signal_handler(signum, frame):
    """信号处理函数"""
    print("\n正在停止所有进程...")
    for proc in global_processes:
        try:
            if sys.platform == "win32":
                proc.kill()
            else:
                proc.terminate()
        except (OSError, ProcessLookupError):
            pass
    sys.exit(0)


if sys.platform != "win32":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def run_py_spy(args: list[str]) -> subprocess.Popen:
    """运行 py-spy 命令"""
    cmd = ["py-spy"] + args
    print(f"执行命令: {' '.join(cmd)}")

    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
            startupinfo=startupinfo,
        )
    else:
        proc = subprocess.Popen(
            cmd,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    global_processes.append(proc)
    return proc


def monitor_top(pid: int, duration: Optional[int] = None):
    """实时监控模式 (类似于 top)"""
    cmd = ["top", "--pid", str(pid)]
    if duration:
        cmd.extend(["--duration", str(duration)])
    proc = run_py_spy(cmd)
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n停止监控...")
        kill_process_tree(pid)
        proc.terminate()
        proc.wait()


def record_profile(
    pid: int,
    output: str,
    duration: Optional[int] = None,
    rate: int = 100,
):
    """记录性能数据到文件"""
    cmd = [
        "record",
        "-o", output,
        "--rate", str(rate),
        "--pid", str(pid),
    ]
    if duration:
        cmd.extend(["--duration", str(duration)])
    proc = run_py_spy(cmd)
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n停止记录...")
        kill_process_tree(pid)
        proc.terminate()
        proc.wait()


def dump_stack(pid: int):
    """转储当前堆栈信息"""
    cmd = ["dump", "--pid", str(pid)]
    run_py_spy(cmd).wait()


def start_app_and_monitor(port: int = 8000, app_module: str = "app.api.main:app"):
    """启动应用并开始监控"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    app_cmd = [
        str(VENV_PYTHON),
        "-m", "uvicorn",
        app_module,
        "--host", "0.0.0.0",
        "--port", str(port),
        "--workers", "1",
    ]

    print(f"启动应用: {' '.join(app_cmd)}")

    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        app_process = subprocess.Popen(
            app_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            startupinfo=startupinfo,
        )
    else:
        app_process = subprocess.Popen(
            app_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

    global_processes.append(app_process)

    try:
        print("等待应用启动...")
        pid = wait_for_app_start(port, timeout=30)
        if not pid:
            print("应用启动超时")
            return

        print(f"应用已启动，PID: {pid}")
        print("开始性能监控 (按 Ctrl+C 停止)...")

        monitor_top(pid)

    except KeyboardInterrupt:
        print("\n停止监控...")
    finally:
        print("停止应用...")
        kill_process_tree(app_process.pid)


def main():
    parser = argparse.ArgumentParser(
        description="FastAPI 应用性能监控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--pid", "-p",
        type=int,
        help="要监控的进程 PID",
    )

    parser.add_argument(
        "--port", "-P",
        type=int,
        default=8000,
        help="应用端口 (默认: 8000)",
    )

    parser.add_argument(
        "--wait", "-w",
        action="store_true",
        help="等待应用启动",
    )

    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=30,
        help="等待应用启动的超时时间 (默认: 30秒)",
    )

    parser.add_argument(
        "--start", "-s",
        action="store_true",
        help="启动应用并自动监控",
    )

    parser.add_argument(
        "--duration", "-d",
        type=int,
        help="监控持续时间 (秒)",
    )

    parser.add_argument(
        "--record", "-r",
        action="store_true",
        help="记录性能数据到文件",
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=str(SPY_DATA_DIR / "profile.svg"),
        help=f"输出文件路径 (默认: {SPY_DATA_DIR}/profile.svg)",
    )

    parser.add_argument(
        "--dump", "-D",
        action="store_true",
        help="转储当前堆栈信息并退出",
    )

    parser.add_argument(
        "--rate",
        type=int,
        default=100,
        help="采样频率 (默认: 100Hz)",
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有 Uvicorn 进程",
    )

    args = parser.parse_args()

    if args.list:
        processes = find_uvicorn_processes()
        if processes:
            print("找到以下 Uvicorn 进程:")
            for proc in processes:
                print(f"  PID: {proc['pid']}, 命令: {proc['cmdline'][:80]}...")
        else:
            print("未找到 Uvicorn 进程")
        return

    if args.start:
        start_app_and_monitor(args.port)
        return

    pid = args.pid
    if not pid and args.port:
        pid = find_process_by_port(args.port)
    if not pid:
        processes = find_uvicorn_processes()
        if processes:
            pid = processes[0]["pid"]
            print(f"自动选择进程 PID: {pid}")
        else:
            print("错误: 未找到目标进程")
            print("请使用 --pid, --port 或 --list 指定进程")
            sys.exit(1)

    if args.wait:
        pid = wait_for_app_start(args.port, args.timeout)
        if not pid:
            print("错误: 等待应用启动超时")
            sys.exit(1)
        print(f"找到进程 PID: {pid}")

    if args.dump:
        dump_stack(pid)
    elif args.record:
        record_profile(pid, args.output, args.duration, args.rate)
    else:
        monitor_top(pid, args.duration)


if __name__ == "__main__":
    main()
