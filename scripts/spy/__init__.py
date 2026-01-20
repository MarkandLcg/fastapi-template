"""
py-spy 性能监控工具包

提供完整的性能监控和分析功能，用于检测 FastAPI 应用的性能瓶颈。

主要模块:
    - monitor: 性能监控脚本，支持实时监控和记录
    - report: 性能报告生成工具
    - config: 配置管理
"""

from .monitor import (
    find_uvicorn_processes,
    find_process_by_port,
    wait_for_app_start,
    monitor_top,
    record_profile,
    dump_stack,
    start_app_and_monitor,
    main as monitor_main,
)

from .report import (
    PerformanceReportGenerator,
    main as report_main,
)

__version__ = "1.0.0"

__all__ = [
    "find_uvicorn_processes",
    "find_process_by_port",
    "wait_for_app_start",
    "monitor_top",
    "record_profile",
    "dump_stack",
    "start_app_and_monitor",
    "monitor_main",
    "PerformanceReportGenerator",
    "report_main",
]
