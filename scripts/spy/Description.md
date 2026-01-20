# py-spy 性能监控工具代码详解

为了帮助你更好地理解这个性能监控工具的工作原理，本文档将逐个文件、逐行代码进行详细解释。即使你之前没有接触过性能分析工具，通过这篇指南，你也能掌握整个系统的核心概念和实现细节。

## 一、整体架构概述

在深入代码细节之前，我们先从宏观角度理解这个工具是如何工作的。整个系统由三个核心模块组成，它们各司其职，共同完成性能监控任务。

**monitor.py** 是整个系统的主入口，负责与 py-spy 工具进行交互，采集运行程序的性能数据。它就像一个控制面板，可以启动监控、记录数据、列出进程等。

**report.py** 负责将采集到的原始性能数据转化为人类可读的报告。它就像一个翻译官，把技术性的性能数据转换成易于理解的文字和图表。

**config.py** 管理所有配置选项，包括监控端口、输出路径、采样频率等。它就像一个说明书，告诉其他模块应该按照什么规则运行。

## 二、config.py 配置文件详解

这个文件定义了所有可配置的参数，就像一个控制面板上的旋钮和开关。理解这个文件是掌握整个工具的第一步。

### 2.1 模块结构和导入

```python
"""
性能监控配置模块

提供默认配置和配置加载功能
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
```

开头的三引号字符串是文档字符串，描述了这个模块的作用。这里使用了 `dataclass` 装饰器，这是 Python 3.7+ 引入的特性，它能自动为我们生成 `__init__`、`__repr__` 等方法，大大简化了类的定义。`Path` 是 Python 标准库中处理文件路径的类，它能跨平台地处理路径分隔符等问题。`typing` 模块中的 `Optional` 用于声明可以是某种类型或 `None` 的参数。

### 2.2 全局常量定义

```python
# 默认数据输出目录
SPY_DATA_DIR = Path(__file__).parent / "data"
```

这段代码定义了默认的数据输出目录。`Path(__file__)` 获取当前文件（config.py）的完整路径，`.parent` 获取其父目录（即 scripts/spy/），然后通过 `/ "data"` 拼接出 data 目录的完整路径。这种方式确保了无论项目安装在什么位置，输出目录都能正确指向 scripts/spy/data 文件夹。

### 2.3 数据类定义

```python
@dataclass
class MonitorConfig:
    """监控配置"""
    port: int = 8000
    timeout: int = 30
    duration: Optional[int] = None
    output: str = str(SPY_DATA_DIR / "profile.svg")
    rate: int = 100
    show_idle: bool = False
    subprocess: bool = False
    locals_depth: int = 3

    app_module: str = "main:app"
    workers: int = 1
```

`MonitorConfig` 是一个数据类，它定义了所有与性能监控相关的配置参数。每个字段后面的值就是默认值，用户可以在运行时通过命令行参数或环境变量覆盖这些默认值。

`port: int = 8000` 指定了 FastAPI 应用默认运行的端口号。当我们运行 `python monitor.py --start` 时，脚本会尝试在这个端口上找到正在运行的应用。

`timeout: int = 30` 是等待应用启动的超时时间，单位是秒。如果在这个时间内应用还没有启动，脚本就会放弃等待并报错。

`duration: Optional[int] = None` 指定监控的持续时间。`Optional[int]` 意味着这个值可以是整数，也可以是 `None`（表示无限运行）。

`output: str = str(SPY_DATA_DIR / "profile.svg")` 指定性能数据的输出文件路径。这里使用了之前定义的 `SPY_DATA_DIR`，默认情况下数据会保存到 scripts/spy/data/profile.svg。

`rate: int = 100` 是采样频率，单位是赫兹（Hz）。这意味着 py-spy 每秒会对程序进行 100 次采样。采样频率越高，获得的数据越精确，但同时也会产生更多的性能开销。

`show_idle: bool = False` 控制是否显示空闲（idle）状态的时间。设为 True 时，火焰图中会包含程序等待的时间，这在某些场景下可能有用，但通常我们更关心实际运行中的性能瓶颈。

`subprocess: bool = False` 控制是否监控子进程。如果设为 True，py-spy 会同时监控由主进程派生的所有子进程。

`locals_depth: int = 3` 控制堆栈跟踪中显示的局部变量层级。较大的值可以提供更多调试信息，但会增加输出数据的复杂度。

`app_module: str = "main:app"` 指定要启动的 FastAPI 应用模块。这是 uvicorn 启动参数的一部分，格式为「模块路径:应用对象」。

`workers: int = 1` 指定 uvicorn 启动的工作进程数量。通常在生产环境中会设置多个 workers 以提高并发处理能力，但在性能分析时，我们通常只使用 1 个 worker，以便更容易追踪问题。

```python
@dataclass
class ReportConfig:
    """报告配置"""
    format: str = "text"
    top_functions: int = 20
    output: Optional[str] = None
```

`ReportConfig` 定义了性能报告相关的配置。`format: str = "text"` 指定输出格式，默认为纯文本格式，也可以设为 "html" 生成网页报告。`top_functions: int = 20` 指定在报告中显示的热点函数数量上限。`output: Optional[str] = None` 指定输出文件路径，设为 None 时会使用默认路径。

### 2.4 配置管理类

```python
class Config:
    """配置管理类"""

    def __init__(self):
        self.monitor = MonitorConfig()
        self.report = ReportConfig()
```

`Config` 类是一个配置容器，它包含两个子配置对象：`monitor` 和 `report`。在 `__init__` 方法中，我们创建了这两个子配置的默认实例。

```python
    def from_env(self) -> "Config":
        """从环境变量加载配置"""
        if os.getenv("SPY_PORT"):
            self.monitor.port = int(os.getenv("SPY_PORT"))
        if os.getenv("SPY_TIMEOUT"):
            self.monitor.timeout = int(os.getenv("SPY_TIMEOUT"))
        if os.getenv("SPY_DURATION"):
            self.monitor.duration = int(os.getenv("SPY_DURATION"))
        if os.getenv("SPY_OUTPUT"):
            self.monitor.output = os.getenv("SPY_OUTPUT")
        if os.getenv("SPY_RATE"):
            self.monitor.rate = int(os.getenv("SPY_RATE"))
        if os.getenv("SPY_APP_MODULE"):
            self.monitor.app_module = os.getenv("SPY_APP_MODULE")
        if os.getenv("SPY_REPORT_FORMAT"):
            self.report.format = os.getenv("SPY_REPORT_FORMAT")

        return self
```

`from_env` 方法允许用户通过环境变量覆盖默认配置。这种设计使得在容器化部署或 CI/CD 环境中配置应用变得更加方便。例如，设置环境变量 `SPY_PORT=8080` 就会将监控端口改为 8080。

```python
    def save(self, path: Path):
        """保存配置到文件"""
        import json

        config_data = {
            "monitor": {
                "port": self.monitor.port,
                "timeout": self.monitor.timeout,
                "duration": self.monitor.duration,
                "output": self.monitor.output,
                "rate": self.monitor.rate,
                "show_idle": self.monitor.show_idle,
                "subprocess": self.monitor.subprocess,
                "locals_depth": self.monitor.locals_depth,
                "app_module": self.monitor.app_module,
                "workers": self.monitor.workers,
            },
            "report": {
                "format": self.report.format,
                "top_functions": self.report.top_functions,
                "output": self.report.output,
            },
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
```

`save` 方法将当前配置保存为 JSON 格式的文件。JSON 是一种广泛使用的数据交换格式，它结构清晰、易于阅读和编写。`indent=2` 参数使输出的 JSON 文件有良好的缩进，便于人工阅读；`ensure_ascii=False` 确保中文字符能正确保存而不会被转义为 Unicode 转义序列。

```python
    @classmethod
    def load(cls, path: Path) -> "Config":
        """从文件加载配置"""
        import json

        config = cls()

        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            if "monitor" in config_data:
                monitor_data = config_data["monitor"]
                config.monitor.port = monitor_data.get("port", config.monitor.port)
                config.monitor.timeout = monitor_data.get("timeout", config.monitor.timeout)
                config.monitor.duration = monitor_data.get("duration")
                config.monitor.output = monitor_data.get("output", config.monitor.output)
                config.monitor.rate = monitor_data.get("rate", config.monitor.rate)
                config.monitor.show_idle = monitor_data.get("show_idle", config.monitor.show_idle)
                config.monitor.subprocess = monitor_data.get("subprocess", config.monitor.subprocess)
                config.monitor.locals_depth = monitor_data.get("locals_depth", config.monitor.locals_depth)
                config.monitor.app_module = monitor_data.get("app_module", config.monitor.app_module)
                config.monitor.workers = monitor_data.get("workers", config.monitor.workers)

            if "report" in config_data:
                report_data = config_data["report"]
                config.report.format = report_data.get("format", config.report.format)
                config.report.top_functions = report_data.get("top_functions", config.report.top_functions)
                config.report.output = report_data.get("output")

        return config
```

`load` 是一个类方法，用于从 JSON 文件加载配置。它首先创建一个包含默认值的配置对象，然后读取文件中的配置值，并使用 `get` 方法安全地更新这些值。如果文件中没有某个配置项，就使用默认值。这种设计确保了即使配置文件不完整，程序也能正常运行。

### 2.5 便捷函数

```python
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.json"


def get_config(config_path: Optional[Path] = None) -> Config:
    """获取配置"""
    path = config_path or DEFAULT_CONFIG_PATH
    config = Config.load(path)
    config.from_env()
    return config


def save_default_config():
    """保存默认配置"""
    config = Config()
    config.save(DEFAULT_CONFIG_PATH)
    print(f"默认配置已保存到: {DEFAULT_CONFIG_PATH}")
```

最后这两个函数提供了便捷的接口。`get_config` 获取配置对象，它会先从文件加载，再从环境变量覆盖，最后返回完整的配置。`save_default_config` 保存默认配置到指定位置，这在用户需要重置配置时很有用。

## 三、monitor.py 监控脚本详解

这个脚本是整个系统的核心，它直接与 py-spy 工具交互，执行实际的性能监控任务。与早期版本相比，当前版本增加了许多重要的改进，包括完善的进程管理、跨平台支持和优雅的信号处理。

### 3.1 模块导入和初始化

```python
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
```

第一行 `#!/usr/bin/env python3` 是 Unix 系统的 shebang，它告诉系统使用 Python 3 来执行这个脚本。文档字符串中详细列出了这个脚本的使用方法，这对于命令行工具来说非常重要，因为用户可以通过 `--help` 参数或直接阅读文档了解如何使用。

```python
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
```

导入的模块各有其用途。`argparse` 是 Python 标准库中用于解析命令行参数的模块；`subprocess` 用于执行外部命令（如 py-spy）；`signal` 用于处理信号（如 Ctrl+C 中断）；`time` 提供时间相关的功能；`psutil` 是一个跨平台的库，用于获取系统和进程的信息。

我们使用 try-except 来检查 psutil 是否已安装。如果没有安装，程序会打印错误信息并退出。这是处理可选依赖的常见模式。

```python
PROJECT_ROOT = Path(__file__).parent.parent.parent
SPY_DATA_DIR = PROJECT_ROOT / "scripts" / "spy" / "data"
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
if sys.platform != "win32":
    VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"

global_processes = []
```

这些路径变量确保脚本能在不同的操作系统上正确运行。`PROJECT_ROOT` 是项目根目录，通过当前文件路径向上追溯三层得到（scripts/spy/ 向上是 scripts/，再向上是项目根目录）。`SPY_DATA_DIR` 是性能数据输出目录。`VENV_PYTHON` 是项目虚拟环境中的 Python 解释器路径，根据不同的操作系统选择不同的路径。

`global_processes` 是一个全局列表，用于跟踪所有由脚本启动的子进程。这对于后续的统一管理和清理非常重要，确保程序退出时能正确终止所有相关进程。

### 3.2 进程查找函数

```python
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
```

这个函数用于查找系统中所有运行 uvicorn 的进程。`psutil.process_iter` 迭代系统中所有的进程，`["pid", "name", "cmdline"]` 参数指定我们只需要获取这些信息，这比获取所有信息更高效。

在循环中，我们检查每个进程的启动命令行（cmdline）是否包含 "uvicorn"。如果包含，就将进程信息添加到结果列表中。`try-except` 块处理两种常见异常：`NoSuchProcess` 表示进程在检查时已经结束；`AccessDenied` 表示没有权限访问该进程的信息。

```python
def find_process_by_port(port: int) -> Optional[int]:
    """根据端口查找进程 PID"""
    for conn in psutil.net_connections():
        if conn.status == "LISTEN" and conn.laddr.port == port:
            return conn.pid
    return None
```

这个函数通过监听端口查找进程。`psutil.net_connections()` 返回所有网络连接信息。我们遍历这些连接，找到状态为 "LISTEN"（正在监听）且端口匹配的连接，返回对应的进程 ID。如果找不到，返回 `None`。

```python
def wait_for_app_start(port: int, timeout: int = 30) -> Optional[int]:
    """等待应用启动并返回 PID"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        pid = find_process_by_port(port)
        if pid:
            return pid
        time.sleep(0.5)
    return None
```

这个函数等待应用在指定端口上启动。它使用一个循环，每隔 0.5 秒检查一次端口，直到找到进程或超时。如果成功找到进程，返回 PID；否则返回 `None`。

### 3.3 进程终止函数

```python
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
```

`kill_process_tree` 是一个重要的增强函数，它实现了优雅的进程树终止。与简单地终止单个进程不同，这个函数会首先终止所有子进程，然后终止父进程。这种设计确保了不会留下孤立的子进程。

函数的工作流程是：首先获取指定 PID 的进程对象，然后使用 `children(recursive=True)` 获取所有子进程（包括嵌套的孙进程）。接着依次发送 `terminate` 信号给子进程，等待它们结束。如果超时后仍有进程存活，则发送 `kill` 信号强制终止。最后同样方式处理父进程。

如果 `psutil` 操作失败（如进程不存在），函数会尝试使用操作系统原生的方式终止进程：Windows 下使用 `taskkill` 命令，Unix 系统使用 `SIGTERM` 信号。这种多层保护确保了进程总能被正确终止。

### 3.4 信号处理函数

```python
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
```

`signal_handler` 是另一个重要的增强功能，它处理用户中断信号（如 Ctrl+C）。当用户按下 Ctrl+C 时，系统会发送 `SIGINT` 信号，这个函数会被调用来清理所有启动的进程。

函数遍历 `global_processes` 列表，对每个进程发送终止信号。Windows 和 Unix 系统使用不同的方法是因为它们对进程信号的处理方式不同。清理完成后，程序正常退出。

```python
if sys.platform != "win32":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
```

这段代码只对非 Windows 系统注册信号处理器。在 Windows 中，信号处理的行为有所不同，Ctrl+C 事件会触发 `KeyboardInterrupt` 异常，我们已经在 `main` 函数的 try-except 块中处理了这种情况。

### 3.5 py-spy 执行函数

```python
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
```

这个函数是整个脚本的核心，它负责执行 py-spy 命令。`args` 是一个参数列表，例如 `["record", "-o", "output.svg", "--pid", "12345"]`。我们在这个列表前加上 "py-spy" 组成完整的命令，然后使用 `subprocess.Popen` 执行。

这个函数的一个重要改进是添加了 Windows 平台支持。在 Windows 上，我们需要设置 `STARTUPINFO` 并设置 `STARTF_USESHOWWINDOW` 标志，这可以防止控制台窗口闪烁，并确保输出正确重定向。

执行后，新创建的进程对象会被添加到 `global_processes` 列表中，这样在程序退出时就能正确清理所有进程。

### 3.6 监控功能函数

```python
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
```

`monitor_top` 启用 py-spy 的实时监控模式，类似于 Linux 的 `top` 命令。它显示当前正在运行的函数列表，以及每个函数占用的 CPU 时间比例。`--duration` 参数可以限制监控的时长。

这个函数的一个重要改进是添加了完善的异常处理。当用户按下 Ctrl+C 触发 `KeyboardInterrupt` 时，函数会先尝试终止目标进程，然后等待 py-spy 进程结束，确保不会留下任何残留进程。

```python
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
```

`record_profile` 是最常用的功能，它将性能数据记录到文件。`record` 是 py-spy 的子命令，用于录制性能数据。`-o` 指定输出文件路径，`--rate` 设置采样频率（默认 100Hz，即每秒采样 100 次），`--pid` 指定要监控的进程 ID。

与 `monitor_top` 类似，这个函数也添加了完善的异常处理，确保在用户中断时能正确清理进程。

```python
def dump_stack(pid: int):
    """转储当前堆栈信息"""
    cmd = ["dump", "--pid", str(pid)]
    run_py_spy(cmd).wait()
```

`dump_stack` 获取进程当前的函数调用栈快照并打印。这在排查某些瞬时问题时很有用。它使用 py-spy 的 `dump` 子命令，然后调用 `.wait()` 等待命令执行完毕。

```python
def start_app_and_monitor(port: int = 8000, app_module: str = "main:app"):
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
```

这个函数一体化地完成「启动应用 → 等待启动 → 开始监控」的全流程。首先，它构建启动 uvicorn 的命令，使用当前项目的虚拟环境 Python 解释器来运行 uvicorn，并指定应用模块和端口。然后调用 `subprocess.Popen` 启动应用进程。

`env` 字典设置了运行环境，其中 `PYTHONPATH` 确保 Python 能找到项目中的模块。`stdout` 和 `stderr` 被重定向到管道，这样应用的日志不会干扰我们的监控输出。

这个函数的一个重要改进是添加了 Windows 平台支持和更完善的进程管理。新启动的进程会被添加到 `global_processes` 列表中，确保程序退出时能被正确清理。`finally` 块确保无论监控是否正常结束，应用进程都会被终止。

### 3.7 命令行参数解析

```python
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
```

`main` 函数使用 `argparse` 模块解析命令行参数。这个模块提供了强大且易于使用的命令行参数解析功能。我们定义了多个参数，包括 PID、端口、等待超时、启动模式、记录模式等。

值得注意的是新增的 `--rate` 参数，它允许用户自定义采样频率。较高的采样频率可以提供更精确的性能数据，但也会产生更多的性能开销。

```python
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
```

解析完参数后，`main` 函数根据参数执行相应的操作。如果指定了 `--list`，则列出所有 Uvicorn 进程；如果指定了 `--start`，则启动应用并监控。

对于其他模式，函数首先尝试确定目标进程的 PID。用户可以通过 `--pid` 直接指定，也可以通过 `--port` 查找。如果两者都没指定，函数会自动选择找到的第一个 Uvicorn 进程。

确定 PID 后，根据用户选择的模式执行相应的监控操作：dump 模式转储堆栈，record 模式记录性能数据，否则进入实时监控模式。

## 四、report.py 报告生成脚本详解

这个脚本负责将 py-spy 采集的原始性能数据转化为易于理解的报告。它支持多种输出格式，包括纯文本和 HTML。

### 4.1 模块导入和初始化

```python
#!/usr/bin/env python3
"""
性能分析报告生成工具

分析 py-spy 生成的性能数据，生成详细的性能报告

使用方法:
    python scripts/spy/report.py profile.svg
    python scripts/spy/report.py profile.svg --format html --output report.html
"""
```

文档字符串提供了使用说明和示例。

```python
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional
```

导入的模块包括：`argparse` 用于命令行参数解析；`json` 用于处理 JSON 格式数据；`sys` 用于系统操作；`defaultdict` 是 `collections` 模块中的一个字典子类，它提供一个默认值；`Path` 用于处理文件路径；`Optional` 用于类型提示。

### 4.2 性能报告生成器类

```python
class PerformanceReportGenerator:
    def __init__(self, profile_file: str):
        self.profile_file = Path(profile_file)
        self.data: dict[str, int] = defaultdict(int)
        self.load_data()
```

`PerformanceReportGenerator` 是核心类，负责解析和分析性能数据。初始化时接收性能数据文件路径，并调用 `load_data` 方法加载数据。

```python
    def load_data(self):
        """加载性能数据"""
        if self.profile_file.suffix == ".svg":
            self._parse_svg()
        elif self.profile_file.suffix in {".json", ".raw"}:
            self._parse_json()
        else:
            print(f"不支持的文件格式: {self.profile_file}")
            sys.exit(1)
```

`load_data` 方法根据文件后缀选择合适的解析方法。py-spy 可以生成 SVG 火焰图和 JSON 格式的数据，这个方法能处理这两种格式。

```python
    def _parse_svg(self):
        """解析 SVG 火焰图文件"""
        try:
            import re
            with open(self.profile_file, 'r', encoding='utf-8') as f:
                content = f.read()

            pattern = r'<g[^>]*>\s*<title>([^<]+)\s*\(\d+\s*samples[^<]*</title>'
            matches = re.findall(pattern, content)

            for func_name in matches:
                self.data[func_name.strip()] += 1

        except Exception as e:
            print(f"解析 SVG 文件时出错: {e}")
            sys.exit(1)
```

`_parse_svg` 方法使用正则表达式解析 SVG 火焰图文件。SVG 文件中的每个函数调用都会在 `<title>` 标签中记录，我们提取这些信息并统计每个函数的出现次数。

```python
    def _parse_json(self):
        """解析 JSON 格式的性能数据"""
        try:
            with open(self.profile_file, 'r') as f:
                for line in f:
                    if '\t' in line:
                        parts = line.strip().split('\t')
                        if len(parts) >= 2:
                            func = parts[0]
                            count = int(parts[1])
                            self.data[func] += count
        except Exception as e:
            print(f"解析 JSON 文件时出错: {e}")
            sys.exit(1)
```

`_parse_json` 方法处理 JSON 格式的性能数据。py-spy 的 JSON 输出通常每行包含一个函数调用及其采样次数，我们按行读取并累加统计。

### 4.3 数据分析

```python
    def analyze(self) -> dict:
        """分析性能数据"""
        total = sum(self.data.values())
        sorted_data = sorted(self.data.items(), key=lambda x: x[1], reverse=True)

        analysis = {
            "total_samples": total,
            "unique_functions": len(self.data),
            "top_functions": [],
            "categories": defaultdict(int),
        }

        for func, count in sorted_data[:50]:
            percentage = (count / total * 100) if total > 0 else 0
            analysis["top_functions"].append({
                "function": func,
                "samples": count,
                "percentage": round(percentage, 2),
            })

            category = self._categorize_function(func)
            analysis["categories"][category] += count

        return analysis
```

`analyze` 方法对加载的性能数据进行深入分析。它计算总采样数、唯一函数数，并按采样次数排序找出热点函数。同时，它还会将函数分类到不同的类别中（如数据库操作、异步 IO 等）。

```python
    def _categorize_function(self, func: str) -> str:
        """分类函数"""
        func_lower = func.lower()

        if any(kw in func_lower for kw in ["await", "coroutine", "async"]):
            return "async_io"
        elif any(kw in func_lower for kw in ["sql", "query", "mysql", "select", "insert"]):
            return "database"
        elif any(kw in func_lower for kw in ["redis", "cache", "get", "set"]):
            return "cache"
        elif any(kw in func_lower for kw in ["uvicorn", "httptools", "request"]):
            return "http"
        elif any(kw in func_lower for kw in ["security", "jwt", "auth"]):
            return "security"
        elif any(kw in func_lower for kw in ["render", "template", "json"]):
            return "serialization"
        else:
            return "other"
```

`_categorize_function` 根据函数名将其归类到不同的性能类别。这种分类有助于快速识别性能瓶颈的来源，比如是数据库操作太慢还是异步 IO 效率不高。

### 4.4 报告生成

```python
    def generate_text_report(self) -> str:
        """生成文本格式报告"""
        analysis = self.analyze()

        lines = [
            "=" * 60,
            "性能分析报告",
            "=" * 60,
            f"总采样数: {analysis['total_samples']}",
            f"唯一函数数: {analysis['unique_functions']}",
            "",
            "-" * 60,
            "按类别分布:",
            "-" * 60,
        ]

        total = analysis["total_samples"]
        for category, count in sorted(analysis["categories"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"  {category:15s}: {count:8d} ({percentage:5.1f}%)")

        lines.extend([
            "",
            "-" * 60,
            "Top 20 热点函数:",
            "-" * 60,
        ])

        for i, func_data in enumerate(analysis["top_functions"][:20], 1):
            lines.append(
                f"{i:2d}. {func_data['function'][:40]:40s} "
                f"{func_data['samples']:8d} ({func_data['percentage']:5.1f}%)"
            )

        lines.extend([
            "",
            "=" * 60,
            "优化建议:",
            "=" * 60,
        ])

        lines.extend(self._generate_recommendations(analysis))

        return "\n".join(lines)
```

`generate_text_report` 生成纯文本格式的性能报告。报告包含总览信息、类别分布饼图、热点函数列表和优化建议。文本格式适合在终端中快速查看或在日志中保存。

```python
    def _generate_recommendations(self, analysis: dict) -> list[str]:
        """生成优化建议"""
        recommendations = []
        total = analysis["total_samples"]
        categories = analysis["categories"]

        if total == 0:
            return ["未收集到足够的性能数据"]

        for category, count in categories.items():
            percentage = (count / total * 100) if total > 0 else 0

            if category == "database" and percentage > 20:
                recommendations.extend([
                    f"数据库操作占用 {percentage:.1f}% CPU:",
                    "   - 检查是否有 N+1 查询问题",
                    "   - 考虑添加数据库连接池",
                    "   - 优化慢查询，添加必要的索引",
                ])
            elif category == "async_io" and percentage > 30:
                recommendations.extend([
                    f"异步操作占用 {percentage:.1f}% CPU:",
                    "   - 检查是否有阻塞性操作",
                    "   - 考虑使用更高效的异步库",
                ])
            elif category == "cache" and percentage > 15:
                recommendations.extend([
                    f"缓存操作占用 {percentage:.1f}% CPU:",
                    "   - 检查缓存命中率",
                    "   - 考虑使用本地缓存减少 Redis 访问",
                ])

        if not recommendations:
            recommendations.append("应用性能良好，未发现明显瓶颈")

        return recommendations
```

`_generate_recommendations` 根据分析结果生成针对性的优化建议。如果某个类别的占比超过阈值（数据库操作超过 20%，异步 IO 超过 30%，缓存操作超过 15%），就会生成相应的优化建议。

```python
    def generate_html_report(self, output_file: str):
        """生成 HTML 格式报告"""
        analysis = self.analyze()

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>性能分析报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .chart-container {{
            margin: 20px 0;
        }}
        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .bar-item {{
            display: flex;
            align-items: center;
        }}
        .bar-label {{
            width: 120px;
            font-size: 14px;
            color: #333;
        }}
        .bar-track {{
            flex: 1;
            height: 25px;
            background: #eee;
            border-radius: 12px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: bold;
            font-size: 12px;
            transition: width 0.5s ease;
        }}
        .function-list {{
            margin-top: 20px;
        }}
        .function-item {{
            display: flex;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }}
        .function-item:hover {{
            background: #f8f9fa;
        }}
        .function-rank {{
            width: 30px;
            font-weight: bold;
            color: #667eea;
        }}
        .function-name {{
            flex: 1;
            font-family: monospace;
            color: #333;
        }}
        .function-stats {{
            text-align: right;
        }}
        .function-samples {{
            font-weight: bold;
            color: #333;
        }}
        .function-percent {{
            color: #666;
            font-size: 0.9em;
        }}
        .recommendations {{
            margin-top: 20px;
        }}
        .recommendation {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
        }}
        .recommendation.warning {{
            border-left-color: #ffc107;
            background: #fff8e1;
        }}
        .recommendation.success {{
            border-left-color: #28a745;
            background: #e8f5e9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>性能分析报告</h1>
            <p>分析文件: {self.profile_file.name}</p>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{analysis['total_samples']:,}</div>
                    <div class="stat-label">总采样数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{analysis['unique_functions']:,}</div>
                    <div class="stat-label">唯一函数数</div>
                </div>
            </div>
        </div>
"""
```

`generate_html_report` 生成一个美观的 HTML 格式报告。报告使用现代的 CSS 设计，包含渐变色背景、卡片式布局和动画效果。HTML 格式的报告适合在浏览器中查看和分享。

### 4.5 主函数

```python
def main():
    parser = argparse.ArgumentParser(
        description="性能分析报告生成工具",
    )

    parser.add_argument(
        "profile_file",
        help="py-spy 生成的性能数据文件",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["text", "html"],
        default="text",
        help="输出格式 (默认: text)",
    )

    parser.add_argument(
        "--output", "-o",
        help="输出文件路径",
    )

    args = parser.parse_args()

    if not Path(args.profile_file).exists():
        print(f"错误: 文件不存在: {args.profile_file}")
        sys.exit(1)

    generator = PerformanceReportGenerator(args.profile_file)

    if args.format == "html":
        output_file = args.output or str(Path(args.profile_file).with_suffix(".html"))
        generator.generate_html_report(output_file)
    else:
        print(generator.generate_text_report())
```

`main` 函数是报告生成脚本的入口点。它解析命令行参数，验证输入文件存在，然后根据指定的格式生成报告。默认生成纯文本报告，使用 `--format html` 参数可以生成 HTML 报告。

## 五、常见使用场景

### 5.1 快速启动并监控

```bash
# 启动应用并自动开始监控
python scripts/spy/monitor.py --start --port 8000

# 按 Ctrl+C 停止监控
```

这个命令会自动启动 FastAPI 应用并开始实时性能监控。

### 5.2 记录性能数据

```bash
# 记录 60 秒的性能数据
python scripts/spy/monitor.py --record --duration 60 --output profile.svg

# 生成性能报告
python scripts/spy/report.py profile.svg --format html --output report.html
```

这个组合命令先记录性能数据，然后生成可视化的 HTML 报告。

### 5.3 监控已运行的进程

```bash
# 通过端口查找进程并监控
python scripts/spy/monitor.py --port 8000

# 或直接指定 PID
python scripts/spy/monitor.py --pid 12345
```

这个命令可以监控已经运行的进程，无需重启应用。

### 5.4 列出所有进程

```bash
# 列出所有 Uvicorn 进程
python scripts/spy/monitor.py --list
```

这个命令显示系统中所有正在运行的 Uvicorn 进程及其信息。

## 六、总结

这个性能监控工具通过集成 py-spy、psutil 和自定义的报告生成模块，提供了一个完整的 FastAPI 应用性能分析解决方案。主要特点包括：

1. **完善的进程管理**：通过 `kill_process_tree` 函数确保进程能被正确终止
2. **跨平台支持**：支持 Windows、Linux 和 macOS 系统
3. **优雅的信号处理**：能正确响应用户的中断操作
4. **多种监控模式**：支持实时监控、数据记录和堆栈转储
5. **智能报告生成**：自动分析性能瓶颈并提供优化建议
6. **灵活的配置方式**：支持命令行参数、环境变量和配置文件

通过这个工具，开发者可以快速定位和解决 FastAPI 应用的性能问题，提升应用的运行效率。
