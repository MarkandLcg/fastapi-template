"""
性能监控配置模块

提供默认配置和配置加载功能
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# 默认数据输出目录
SPY_DATA_DIR = Path(__file__).parent / "data"


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


@dataclass
class ReportConfig:
    """报告配置"""
    format: str = "text"
    top_functions: int = 20
    output: Optional[str] = None


class Config:
    """配置管理类"""

    def __init__(self):
        self.monitor = MonitorConfig()
        self.report = ReportConfig()

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
