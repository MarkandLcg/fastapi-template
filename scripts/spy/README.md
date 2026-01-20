# FastAPI Spy 性能监控工具

本工具使用 [py-spy](https://github.com/benfred/py-spy) 对 FastAPI 应用进行性能监控和分析。

## 功能特性

- **实时监控**：实时显示进程的函数调用情况，类似 Linux 的 top 命令
- **性能记录**：记录性能数据生成火焰图
- **堆栈转储**：随时转储进程的当前堆栈信息
- **多模式支持**：支持 PID 监控、端口等待、应用启动等多种模式
- **跨平台支持**：支持 Windows 和 Linux/macOS 系统
- **进程管理**：自动管理子进程，防止进程泄漏
- **报告生成**：自动分析性能数据，生成文本和 HTML 报告
- **智能分类**：自动将函数按类型分类（数据库、缓存、异步等）

## 快速开始

### 1. 安装依赖

```bash
# 安装 py-spy
pip install py-spy

# 安装 psutil (用于进程管理)
pip install psutil
```

### 2. 基本使用方法

```bash
# 方式1: 直接指定进程 PID 监控
uv run scripts/spy/monitor.py --pid 12345

# 方式2: 等待应用启动并自动获取 PID
uv run scripts/spy/monitor.py --wait --timeout 30

# 方式3: 启动应用并自动开始监控
uv run scripts/spy/monitor.py --start --port 8000

# 方式4: 记录性能数据生成火焰图
uv run scripts/spy/monitor.py --record --duration 60 --output scripts/spy/data/perf_data.svg

# 方式5: 列出所有运行中的 Uvicorn 进程
uv run scripts/spy/monitor.py --list

# 方式6: 转储当前堆栈信息
uv run scripts/spy/monitor.py --dump --pid 12345
```

### 3. 生成性能报告

```bash
# 生成文本报告
uv run scripts/spy/report.py scripts/spy/data/perf_data.svg

# 生成 HTML 报告
uv run scripts/spy/report.py scripts/spy/data/perf_data.svg --format html --output scripts/spy/data/report.html     
```

## 架构设计

```
scripts/spy/
├── monitor.py      # 核心监控模块
├── report.py       # 报告生成模块
├── config.py       # 配置管理模块
├── data/           # 性能数据存储目录
└── Description.md  # 工具代码详解
```

### 核心模块职责

#### 1. monitor.py (核心监控模块)

**模块职责**：
- 提供性能监控的命令行接口
- 管理进程的启动、停止和生命周期
- 集成 py-spy 的各种功能（top、record、dump）
- 实现跨平台的进程管理

**关键函数说明**：

- `find_uvicorn_processes()`: 查找所有运行中的 Uvicorn 进程
  - 返回包含 PID、进程名和命令行信息的字典列表
  - 用于 `--list` 功能

- `find_process_by_port(port: int) -> Optional[int]`: 根据端口查找 PID
  - 通过检查网络连接找到监听指定端口的进程
  - 用于 `--wait` 功能和自动检测

- `wait_for_app_start(port: int, timeout: int = 30) -> Optional[int]`: 等待应用启动
  - 轮询检查指定端口是否有进程开始监听
  - 超时返回 None，否则返回 PID

- `kill_process_tree(pid: int)`: 终止进程及其所有子进程
  - 使用 psutil 查找并终止所有子进程
  - 父进程终止前等待子进程结束
  - 提供跨平台回退方案（Windows 用 taskkill，Unix 用 SIGTERM）
  - 处理各种异常情况

- `signal_handler(signum, frame)`: 信号处理函数
  - 处理 SIGINT（Ctrl+C）和 SIGTERM 信号
  - 遍历 `global_processes` 列表终止所有进程
  - 确保程序优雅退出

- `run_py_spy(args: list[str]) -> subprocess.Popen`: 运行 py-spy 命令
  - 构建 py-spy 命令行参数
  - 处理 Windows 平台的窗口隐藏
  - 将进程添加到 `global_processes` 跟踪列表
  - 返回进程对象供控制

- `monitor_top(pid: int, duration: Optional[int] = None)`: 实时监控模式
  - 调用 py-spy top 命令实时显示函数调用
  - 支持 Ctrl+C 中断
  - 中断后自动清理目标进程

- `record_profile(pid: int, output: str, duration: Optional[int] = None, rate: int = 100)`: 记录性能数据
  - 调用 py-spy record 命令记录性能数据
  - 支持指定采样率（--rate）和持续时间
  - 生成 SVG 火焰图或原始数据

- `dump_stack(pid: int)`: 转储堆栈信息
  - 调用 py-spy dump 命令获取当前堆栈
  - 用于调试和分析当前执行状态

- `start_app_and_monitor(port: int = 8000, app_module: str = "main:app")`: 启动并监控应用
  - 启动 Uvicorn 服务器进程
  - 等待应用启动完成
  - 自动开始性能监控
  - 确保退出时正确停止所有进程

- `main()`: 命令行入口
  - 使用 argparse 解析命令行参数
  - 支持多种使用模式
  - 提供详细的使用说明

**命令行参数**：

| 参数 | 短参数 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| --pid | -p | int | None | 要监控的进程 PID |
| --port | -P | int | 8000 | 应用端口 |
| --wait | -w | bool | False | 等待应用启动 |
| --timeout | -t | int | 30 | 等待超时时间（秒） |
| --start | -s | bool | False | 启动应用并监控 |
| --duration | -d | int | None | 监控持续时间（秒） |
| --output | -o | str | profile.svg | 输出文件路径 |
| --record | -r | bool | False | 记录性能数据 |
| --list | -l | bool | False | 列出所有 Uvicorn 进程 |
| --dump | None | bool | False | 转储堆栈信息 |
| --rate | None | int | 100 | 采样率（样本/秒） |

#### 2. config.py (配置管理模块)

**模块职责**：
- 提供集中化的配置管理
- 支持环境变量覆盖
- 配置的序列化和反序列化
- 默认值管理

**关键类说明**：

- `MonitorConfig`: 监控配置数据类
  - `port: int = 8000` - 监控端口
  - `timeout: int = 30` - 启动超时时间
  - `duration: Optional[int] = None` - 监控持续时间
  - `output: str` - 输出文件路径
  - `rate: int = 100` - 采样率
  - `show_idle: bool = False` - 是否显示空闲函数
  - `subprocess: bool = False` - 是否作为子进程运行
  - `locals_depth: int = 3` - 局部变量显示深度
  - `app_module: str = "main:app"` - 应用模块路径
  - `workers: int = 1` - 工作进程数

- `ReportConfig`: 报告配置数据类
  - `format: str = "text"` - 报告格式（text/html）
  - `top_functions: int = 20` - 显示的热点函数数量
  - `output: Optional[str] = None` - 输出文件路径

- `Config`: 配置管理类
  - `monitor: MonitorConfig` - 监控配置实例
  - `report: ReportConfig` - 报告配置实例
  - `from_env()` - 从环境变量加载配置
  - `save(path: Path)` - 保存配置到文件
  - `load(path: Path)` - 从文件加载配置

**环境变量配置**：

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| SPY_PORT | 监控端口 | 8000 |
| SPY_TIMEOUT | 启动超时时间 | 30 |
| SPY_DURATION | 监控持续时间 | None |
| SPY_OUTPUT | 输出文件路径 | profile.svg |
| SPY_RATE | 采样率 | 100 |
| SPY_APP_MODULE | 应用模块路径 | main:app |
| SPY_REPORT_FORMAT | 报告格式 | text |

#### 3. report.py (报告生成模块)

**模块职责**：
- 解析 py-spy 生成的性能数据
- 分析热点函数和性能瓶颈
- 生成可读性好的文本报告
- 生成交互式的 HTML 报告

**关键类说明**：

- `PerformanceReportGenerator`: 性能报告生成器
  - `load_data()`: 加载性能数据
  - `_parse_svg()`: 解析 SVG 火焰图
  - `_parse_json()`: 解析 JSON 格式数据
  - `analyze()`: 分析性能数据
  - `_categorize_function()`: 函数分类
  - `generate_text_report()`: 生成文本报告
  - `generate_html_report()`: 生成 HTML 报告
  - `_generate_recommendations()`: 生成优化建议

**函数分类规则**：

| 分类 | 关键词 | 说明 |
|------|--------|------|
| async_io | await, coroutine, async | 异步操作 |
| database | sql, query, mysql, select, insert | 数据库操作 |
| cache | redis, cache, get, set | 缓存操作 |
| http | uvicorn, httptools, request | HTTP 处理 |
| security | security, jwt, auth | 安全认证 |
| serialization | render, template, json | 数据序列化 |
| other | 其他 | 其他操作 |

## 使用场景

### 场景1：开发环境实时监控

```bash
# 启动应用并实时监控
uv run scripts/spy/monitor.py --start --port 8000
```

### 场景2：生产环境性能分析

```bash
# 记录 60 秒的性能数据
uv run scripts/spy/monitor.py --wait --timeout 30 --record --duration 60 --output perf_data.svg

# 生成分析报告
uv run scripts/spy/report.py perf_data.svg --format html --output report.html
```

### 场景3：排查特定问题

```bash
# 当问题出现时，转储当前堆栈
uv run scripts/spy/monitor.py --dump --pid 12345

# 或持续记录，发现问题后停止
uv run scripts/spy/monitor.py --record --output profile.svg --pid 12345
# 按 Ctrl+C 停止
```

### 场景4：性能回归测试

```bash
# 在代码修改前记录基准数据
uv run scripts/spy/monitor.py --record --duration 60 --output baseline.svg
uv run scripts/spy/report.py baseline.svg --output baseline_report.txt

# 在代码修改后记录新数据
uv run scripts/spy/monitor.py --record --duration 60 --output current.svg
uv run scripts/spy/report.py current.svg --output current_report.txt

# 对比两个报告
```

## 最佳实践

1. **选择合适的采样率**：默认 100 samples/sec 适合大多数场景，高频场景可增加
2. **设置合理的监控时长**：建议 30-60 秒，避免过长导致数据过大
3. **在真实场景测试**：在接近生产环境的负载下进行测试
4. **多次采样取平均**：性能数据有随机性，建议多次采样
5. **关注热点函数**：优先优化占用 CPU 最多的函数
6. **结合业务场景**：结合实际请求分析，而非只看 CPU 占比

## 常见问题

### Q: 权限问题
在 Linux/macOS 上可能需要 root 权限：
```bash
sudo uv run scripts/spy/monitor.py --pid 12345
```

### Q: Windows 上进程无法终止
确保安装了 psutil，脚本会自动使用 taskkill 作为回退方案。

### Q: 火焰图不显示
检查 py-spy 是否正确安装，以及输出文件是否有写入权限。

### Q: 采样率设置多少合适
- 低负载应用：10-50 samples/sec
- 普通应用：100 samples/sec（默认）
- 高负载应用：200-1000 samples/sec

## 输出示例

### 文本报告示例

```
============================================================
性能分析报告
============================================================
总采样数: 15420
唯一函数数: 234

------------------------------------------------------------
按类别分布:
------------------------------------------------------------
  database       :   4567 (29.6%)
  async_io       :   3421 (22.2%)
  serialization  :   2345 (15.2%)
  cache          :   1890 (12.3%)
  http           :   1567 (10.2%)
  other          :   1630 (10.6%)

------------------------------------------------------------
Top 20 热点函数:
------------------------------------------------------------
  1. app.api.routes.users.get_user_info    2345  (15.2%)
  2. app.db.session.execute                 1890  (12.3%)
  3. app.core.cache.redis_get               1234  ( 8.0%)
  4. pydantic.main.model_validate           1023  ( 6.6%)
  ...

============================================================
优化建议:
============================================================
数据库操作占用 29.6% CPU:
   - 检查是否有 N+1 查询问题
   - 考虑添加数据库连接池
   - 优化慢查询，添加必要的索引
```

## 与其他工具的对比

| 特性 | py-spy | cProfile | py-spy (record) |
|------|--------|----------|-----------------|
| 实时监控 | ✓ | ✗ | ✗ |
| 低开销 | ✓ (0.5-2%) | ✗ (5-10%) | ✓ |
| 火焰图 | ✗ | ✗ | ✓ |
| 无需修改代码 | ✓ | ✗ | ✓ |
| 生产环境安全 | ✓ | ✗ | ✓ |
