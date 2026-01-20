"""
性能分析启动脚本

这个脚本的作用：
1. 作为程序入口点
2. 被 Scalene 分析器调用
3. 启动 FastAPI 服务

使用方法：
    # 基础分析
    python -m scalene --html profile_api.py

    # 带参数的分析
    python -m scalene --html profile_api.py --port 8000

    # 内存专项分析
    python -m scalene --memory --html profile_api.py --port 8000
"""

import argparse

import uvicorn


def main():
    """
    主函数：解析参数并启动服务
    """
    parser = argparse.ArgumentParser(
        description="FastAPI 性能分析启动脚本"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务绑定的地址，默认为 0.0.0.0（所有网卡）"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务端口号，默认为 8000"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="工作进程数，开发环境建议用 1"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="是否启用热重载（代码修改后自动重启）"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 启动性能分析模式")
    print("=" * 60)
    print(f"📍 服务地址: http://{args.host}:{args.port}")
    print(f"📊 分析报告: 将在程序结束后生成 HTML 文件")
    print(f"🔧 工作进程: {args.workers}")
    print("=" * 60)
    
    uvicorn.run(
        app="app.main:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
