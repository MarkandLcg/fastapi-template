# FastAPI 模板项目

一个基于 FastAPI 框架开发的现代化 Python Web API 模板项目，提供了完整的用户认证、用户管理等功能，采用模块化设计，易于扩展和维护。

## 🌟 项目特点

- **现代框架**: 使用 FastAPI 框架，提供高性能、自动文档生成等特性
- **完整认证**: 实现了基于 JWT 的用户认证系统，支持登录、注册等功能
- **数据库支持**: 集成 SQLModel (SQLAlchemy + Pydantic) 操作 MySQL 数据库
- **安全机制**: 使用 Argon2 进行密码哈希，确保密码安全
- **模块化设计**: 采用清晰的模块化结构，便于代码维护和扩展
- **环境配置**: 支持多环境配置，使用 Pydantic Settings 管理环境变量
- **CORS 支持**: 配置了跨域资源共享，方便前端集成
- **自动文档**: 内置 Swagger UI 和 ReDoc 接口文档

## 🛠 技术栈

| 技术/框架         | 版本       | 用途               |
| ----------------- | ---------- | ------------------ |
| Python            | >= 3.12    | 开发语言           |
| FastAPI           | >= 0.125.0 | Web 框架           |
| SQLModel          | >= 0.0.27  | ORM 工具           |
| PyMySQL           | >= 1.1.2   | MySQL 驱动         |
| Pydantic Settings | >= 2.12.0  | 配置管理           |
| PyJWT             | >= 2.10.1  | JWT 令牌生成与验证 |
| pwdlib[argon2]    | >= 0.3.0   | 密码哈希           |
| python-multipart  | >= 0.0.21  | 表单数据处理       |
| Uvicorn           | >= 0.38.0  | ASGI 服务器        |

## 📦 项目结构

```
fastapi-template/
├── app/                      # 应用主目录
│   ├── api/                  # API 路由模块
│   │   ├── routes/           # 路由定义
│   │   │   └── v1/           # API v1 版本
│   │   │       ├── __init__.py
│   │   │       ├── login.py  # 登录相关接口
│   │   │       └── users.py  # 用户相关接口
│   │   ├── __init__.py
│   │   ├── deps.py           # 依赖注入
│   │   └── main.py           # API 路由入口
│   ├── core/                 # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py         # 配置管理
│   │   ├── db.py             # 数据库连接
│   │   └── security.py       # 安全相关函数
│   ├── crud/                 # CRUD 操作模块
│   │   ├── __init__.py
│   │   └── users_crud.py     # 用户 CRUD 操作
│   └── models/               # 数据模型
│       ├── __init__.py
│       ├── base_models.py    # 基础模型
│       ├── token_models.py   # 令牌模型
│       └── users_models.py   # 用户模型
├── .env                      # 环境变量配置
├── main.py                   # 应用入口
├── pyproject.toml            # 项目依赖配置
└── uv.lock                   # 依赖版本锁定文件
```

## 🚀 快速开始

### 1. 环境准备

确保你已经安装了 Python 3.12 或更高版本：

```bash
python --version
```

### 2. 安装依赖

使用 pip 或 uv 安装项目依赖：

#### 使用 uv（推荐）

```bash
# 安装 uv（如果未安装）
pip install uv

# 安装项目依赖
uv sync
```

### 3. 配置环境变量

复制或修改 `.env` 文件，根据你的环境配置相关参数：

```bash
# 复制示例配置文件（如果存在）
# cp .env.example .env
```

主要配置项说明：

```
# 环境：local（本地）, staging（暂存）, production（生产）
ENVIRONMENT=local

# API 文档标题
PROJECT_NAME="FastAPI Template"

# 前端主机地址
FRONTEND_HOST=http://localhost:5173

# 后端允许的 CORS 来源
BACKEND_CORS_ORIGINS="http://localhost,http://localhost:5173"

# JWT 密钥（请确保生产环境使用强密钥）
SECRET_KEY=changethis

# MySQL 配置
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_DB=fat_db
MYSQL_USER=root
MYSQL_PASSWORD=password
```

### 4. 启动应用

使用 Uvicorn 启动应用：

```bash
# 直接启动
uvicorn main:app --reload

# 或使用 python 命令启动
python main.py
```

应用启动后，你可以访问以下地址：

- API 文档 (Swagger UI): http://localhost:8000/docs
- API 文档 (ReDoc): http://localhost:8000/redoc
- OpenAPI 规范: http://localhost:8000/api/v1/openapi.json

## 📖 API 文档

应用启动后，可以通过以下方式访问 API 文档：

### Swagger UI

访问 http://localhost:8000/docs 可以看到交互式 API 文档：

- 可以直接在界面上测试 API 接口
- 查看请求参数和响应格式
- 获取 API 调用示例

### ReDoc

访问 http://localhost:8000/redoc 可以看到更简洁的 API 文档：

- 提供清晰的 API 分类和描述
- 适合作为正式文档参考

## 🔧 使用指南

### 用户注册

**接口**: `POST /api/v1/users/register`

**请求体**:

```json
{
  "username": "testuser",
  "password": "testpassword",
  "nickname": "测试用户",
  "email": "test@example.com"
}
```

**响应**:

```json
{
  "code": 200,
  "message": "User registered successfully",
  "data": true
}
```

### 用户登录

**接口**: `POST /api/v1/login/access-token`

**请求体**:

```json
{
  "username": "testuser",
  "password": "testpassword"
}
```

**响应**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 获取当前用户信息

**接口**: `GET /api/v1/users/me`

**请求头**:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应**:

```json
{
  "code": 200,
  "message": "User info retrieved successfully",
  "data": {
    "id": 1,
    "username": "testuser",
    "nickname": "测试用户",
    "email": "test@example.com",
    "phone": null,
    "avatar": null,
    "intro": null,
    "role_id": null,
    "status": true,
    "deleted": false,
    "create_time": "2023-01-01T12:00:00",
    "update_time": "2023-01-01T12:00:00"
  }
}
```

## 📝 开发指南

### 添加新的路由

1. 在 `app/api/routes/v1/` 目录下创建新的路由文件，例如 `items.py`

2. 定义路由和处理函数：

```python
from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
def get_items():
    return {"message": "List of items"}
```

3. 在 `app/api/main.py` 中包含新路由：

```python
from app.api.routes.v1 import items  # 添加导入

api_router.include_router(items.router)  # 添加路由
```

### 添加新的数据模型

1. 在 `app/models/` 目录下创建新的模型文件或在现有文件中添加

2. 定义 SQLModel 模型：

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Item(SQLModel, table=True):
    __tablename__ = "item_t"
    
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str = Field(default=None)
    price: float
    create_time: datetime = Field(default_factory=datetime.utcnow)
```

3. 在 `app/core/db.py` 中导入新模型：

```python
from app.models import items_models  # noqa
```

### 添加新的 CRUD 操作

1. 在 `app/crud/` 目录下创建新的 CRUD 文件，例如 `items_crud.py`

2. 定义 CRUD 函数：

```python
from sqlmodel import Session, select
from app.models.items_models import Item

class ItemCreate(SQLModel):
    name: str
    description: str = None
    price: float

def create_item(session: Session, item: ItemCreate) -> Item:
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def get_item(session: Session, item_id: int) -> Item:
    return session.get(Item, item_id)
```

## 🧪 测试

### 使用 HTTP 客户端测试

你可以使用任何 HTTP 客户端工具（如 Postman、Insomnia 或 curl）测试 API。

#### 示例：使用 curl 测试注册接口

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "testpassword", "nickname": "测试用户"}'
```

#### 示例：使用 curl 测试登录接口

```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=testpassword"
```

## 📦 部署

### 使用 Uvicorn 直接部署

```bash
# 在生产环境中使用多个工作进程
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 使用 Docker 部署

1. 创建 Dockerfile：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv
RUN uv sync --no-dev

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. 创建 docker-compose.yml：

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
  
  db:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=fat_db
```

3. 启动容器：

```bash
docker-compose up -d
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 项目地址：[GitHub Repository](https://github.com/MarkandLcg/fastapi-template)

---

**开始构建你的 FastAPI 应用吧！🚀**