from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.db import create_tables, shutdown_db


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """应用生命周期管理"""
#     # 应用启动时执行
#     print("应用启动中...")
#     create_tables()  # 调用同步函数
#     print("应用启动完成")
#     yield
#     # 应用关闭时执行
#     print("应用关闭中...")
#     shutdown_db()  # 调用同步函数
#     print("应用关闭完成")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 应用启动时执行
    print("应用启动中...")
    await create_tables()  # 调用异步函数
    print("应用启动完成")
    yield
    # 应用关闭时执行
    print("应用关闭中...")
    await shutdown_db()  # 调用异步函数
    print("应用关闭完成")


app = FastAPI(
    title=settings.PROJECT_NAME,  # API 文档标题，来自配置文件
    openapi_url=f"{settings.API_V1_STR}/openapi.json",  # OpenAPI 文档的 URL 路径
    generate_unique_id_function=custom_generate_unique_id,  # 自定义路由 ID 生成函数
    lifespan=lifespan,  # 使用生命周期管理
)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,  # 允许的来源列表，来自配置文件
        allow_credentials=True,  # 允许携带凭证（如 cookies）
        allow_methods=["*"],  # 允许所有 HTTP 方法
        allow_headers=["*"],  # 允许所有 HTTP 头部
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)