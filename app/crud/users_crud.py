from pydantic import BaseModel
# from sqlmodel import Session, select
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, get_password_hash
from app.models.users_models import UserModel


class UserIn(BaseModel):
    """
    用户信息查询内部模型，包含用户基本信息
    """
    username: str
    email: str | None = None
    nickname: str | None = None
    phone: str | None = None
    avatar: str | None = None
    intro: str | None = None
    role_id: int | None = None
    status: bool = True

class UserInfo(UserIn):
    """
    用户信息验证模型，包含用户ID
    """
    id: int

class UserCreate(UserIn):
    """
    用户注册模型，包含用户注册信息
    """
    password: str


# def get_user_by_sub(*, session: Session, sub: str) -> UserInfo | None:
#     """
#     根据 sub 查询用户
#     :param session: 数据库会话
#     :param sub: 用户唯一标识符
#     :return: 用户对象
#     """
#     statement = select(UserModel).where(UserModel.id == int(sub))
#     user = session.exec(statement).first()
#     if user:
#         return UserInfo(**user.__dict__)
#     return None

async def get_user_by_sub(*, session: AsyncSession, sub: str) -> UserInfo | None:
    """
    根据 sub 异步获取用户信息
    :param session: 数据库会话
    :param sub: 用户唯一标识符
    :return: 用户对象
    """
    statement = select(UserModel).where(UserModel.id == int(sub))
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    if user:
        return UserInfo(**user.__dict__)
    return None


# def authenticate(*, session: Session, username: str, password: str) -> UserInfo | None:
#     """
#     验证用户密码
#     :param session: 数据库会话
#     :param username: 用户名
#     :param password: 密码
#     :return: 用户对象
#     """
#     statement = select(UserModel).where(UserModel.username == username)
#     user = session.exec(statement).first()
#     if not user:
#         return None
#     if not verify_password(password, user.password):
#         return None
#     return UserInfo(**user.__dict__)

async def authenticate(*, session: AsyncSession, username: str, password: str) -> UserInfo | None:
    """
    异步验证用户密码
    :param session: 数据库会话
    :param username: 用户名
    :param password: 密码
    :return: 用户对象
    """
    statement = select(UserModel).where(UserModel.username == username)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return UserInfo(**user.__dict__)

# def get_user_by_username(*, session: Session, username: str) -> UserInfo | None:
#     """
#     根据用户名查询用户
#     :param session: 数据库会话
#     :param username: 用户名
#     :return: 用户对象
#     """
#     statement = select(UserModel).where(UserModel.username == username)
#     user = session.exec(statement).first()
#     if user:
#         return UserInfo(**user.__dict__)
#     return None

async def get_user_by_username(*, session: AsyncSession, username: str) -> UserInfo | None:
    """
    根据用户名异步查询用户
    :param session: 数据库会话
    :param username: 用户名
    :return: 用户对象
    """
    statement = select(UserModel).where(UserModel.username == username)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()
    if user:
        return UserInfo(**user.__dict__)
    return None

# def create_user(*, session: Session, user: UserCreate) -> UserModel:
#     """
#     创建新用户
#     :param session: 数据库会话
#     :param user: 用户注册信息
#     :return: 用户对象
#     """
#     # 密码哈希
#     user.password = get_password_hash(user.password)
#     # 创建用户
#     db_user = UserModel(**user.model_dump())
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user

async def create_user(*, session: AsyncSession, user: UserCreate) -> UserModel:
    """
    异步创建新用户
    :param session: 数据库会话
    :param user: 用户注册信息
    :return: 用户对象
    """
    # 密码哈希
    user.password = get_password_hash(user.password)
    # 创建用户
    db_user = UserModel(**user.model_dump())
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user