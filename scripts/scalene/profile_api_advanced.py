"""
高级性能分析启动脚本

这个脚本提供更精细的控制：
1. 可调节采样间隔（精确度 vs 开销）
2. 可选择分析子进程
3. 可排除特定模块

使用方法：
    # 基础使用
    python -m scalene --html profile_api_advanced.py --port 8000
    
    # 高精度采样（开销更大）
    python -m scalene --sample-interval 0.0001 --html profile_api_advanced.py
    
    # 分析子进程
    python -m scalene --profile-children profile_api_advanced.py
    
    # 只分析特定模块
    python -m scalene --profile-re "app\.(api|core)" --html profile_api_advanced.py
"""

import argparse
import os

import uvicorn


def main():
    """
    主函数：解析高级参数并启动服务
    """
    parser = argparse.ArgumentParser(
        description="FastAPI 高级性能分析启动脚本"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务绑定的地址"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务端口号"
    )
    
    parser.add_argument(
        "--sample-interval",
        type=float,
        default=0.001,
        help="采样间隔（秒），越小越精确但开销越大"
    )
    
    parser.add_argument(
        "--profile-children",
        action="store_true",
        help="是否分析子进程（多进程模式下）"
    )
    
    parser.add_argument(
        "--no-profile-re",
        type=str,
        default="",
        help="排除匹配的正则表达式路径（用 | 分隔多个）"
    )
    
    args = parser.parse_args()
    
    if args.sample_interval:
        os.environ["SCALENE_SAMPLE_INTERVAL"] = str(args.sample_interval)
    
    print("=" * 60)
    print("🚀 启动高级性能分析模式")
    print("=" * 60)
    print(f"📍 服务地址: http://{args.host}:{args.port}")
    print(f"⏱️  采样间隔: {args.sample_interval} 秒")
    print(f"👶 分析子进程: {'是' if args.profile_children else '否'}")
    print("=" * 60)
    
    uvicorn.run(
        app="app.main:app",
        host=args.host,
        port=args.port,
        workers=1,
        reload=False,
        log_level="warning"
    )


if __name__ == "__main__":
    main()
