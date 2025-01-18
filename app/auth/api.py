from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.schema import Token, UserRead, UserCreate, UserUpdate
from app.auth.utils import authenticate_user, create_access_token, get_current_active_user, create_user, \
    blacklist_token, get_users, get_user_by_id, update_user, delete_user, read_me, user_get
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_session

from app.auth.utils import oauth2_scheme


router = APIRouter()


@router.post("/login")
async def login(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: get_session,
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный username или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(
        current_user: user_get,
        token: Annotated[str, Depends(oauth2_scheme)],
):
    blacklist_token(token)
    return {"msg": "Успешно вышли из системы"}


router_user = APIRouter()


@router_user.post("/")
async def register_user(
        user: UserCreate,
        db: get_session,
):
    return await create_user(db, user)


@router_user.get("/")
async def get_users_endpoint(
        current_user: user_get,
        db: get_session,
):
    return await get_users(db)


@router_user.get('/{user_id}')
async def get_user_by_id_endpoint(
        user_id: int,
        current_user: user_get,
        db: get_session,
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="У вас нет прав на просмотр пользователей")
    return await get_user_by_id(db, user_id)


@router_user.put('/')
async def update_user_endpoint(
        user: UserUpdate,
        current_user: user_get,
        db: get_session,
):
    return await update_user(db, current_user.id, user)


@router_user.delete('/{user_id}')
async def delete_user_endpoint(
        user_id: int,
        current_user: user_get,
        db: get_session,
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="У вас нет прав на удаление пользователей")
    return await delete_user(db, user_id)


@router.get("/me/", response_model={})
async def read_user_me(
        current_user: Annotated[UserRead, Depends(get_current_active_user)],
        token: Annotated[str, Depends(oauth2_scheme)]
):
    return await read_me(current_user, token)
