from datetime import timedelta, datetime
from typing import Annotated, Set
import pytz

from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.model import User
from app.auth.schema import TokenData, UserRead, UserCreate, UserResponse, UserUpdate
from app.config import SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_async_session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

token_blacklist: Set[str] = set()

def blacklist_token(token: str):
    token_blacklist.add(token)


def is_token_blacklisted(token: str) -> bool:
    return token in token_blacklist


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


async def get_user(db: AsyncSession, username: str):
    res = await db.execute(select(User).filter_by(username=username))
    user = res.scalars().first()
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    current_tz = pytz.timezone('Asia/Tashkent')
    if expires_delta:
        expire = datetime.now(current_tz) + expires_delta
    else:
        expire = datetime.now(current_tz) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_async_session)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if is_token_blacklisted(token):
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserRead, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Неактивный пользователь")
    return current_user


async def create_user(db: AsyncSession, user: UserCreate):

    try:
        print(user)
        hashed_password = get_password_hash(user.hashed_password)

        user = User(
            hashed_password=hashed_password,
            username=user.username,
            full_name=user.full_name,
            is_superuser=False if user.is_superuser else False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserResponse(**user.__dict__)
    except IntegrityError as e:
        await db.rollback()
        if "unique constraint" in str(e.orig):
            raise HTTPException(status_code=400, detail="username пользователя уже существует")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def get_users(db: AsyncSession):
    res = await db.execute(select(User))
    users = res.scalars().all()
    return users or []


async def get_user_by_id(db: AsyncSession, user_id: int):
    res = await db.execute(select(User).filter_by(id=user_id))
    user = res.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь с идентификатором не найден")

    return user


async def update_user(db: AsyncSession, user_id: int, user: UserUpdate):
    res_username = await db.execute(select(User).filter_by(username=user.username))
    user_username = res_username.scalars().first()
    if user_username:
        if user_username.username != user.username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Пользователь с username уже существует')

    user_db = await get_user_by_id(db, user_id)

    try:
        if user.hashed_password:
            hashed_pass = get_password_hash(user.hashed_password)
            user.hashed_password = hashed_pass

        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(user_db, key, value)

        await db.commit()
        return user_db
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user_by_id(db, user_id)
    try:
        await db.delete(user)
        await db.commit()
        return {"detail": "Пользователь успешно удален"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def read_me(current_user, token: Annotated[str, Depends(oauth2_scheme)]):
    payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    current_tz = pytz.timezone('Asia/Tashkent')
    new_expire = datetime.now(current_tz) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    payload['exp'] = new_expire
    new_token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return {"user": current_user, "token": new_token}

user_get = Annotated[UserRead, Depends(get_current_active_user)]

