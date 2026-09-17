from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy import or_, select

from app.core.deps import DbSession
from app.core.security import (
    REFRESH_COOKIE,
    TokenError,
    clear_auth_cookies,
    decode_token,
    hash_password,
    set_auth_cookies,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserPrivate

router = APIRouter(prefix="/auth", tags=["auth"])

# Verified against when a login names a user that doesn't exist, so response time
# doesn't reveal whether the account is real.
_DUMMY_HASH = hash_password("not-a-real-password")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: DbSession, response: Response) -> UserPrivate:
    email = payload.email.lower()
    clash = await db.scalar(
        select(User).where(or_(User.email == email, User.username == payload.username))
    )
    if clash is not None:
        field = "email" if clash.email == email else "username"
        raise HTTPException(status.HTTP_409_CONFLICT, detail=f"That {field} is already taken")

    user = User(
        email=email,
        username=payload.username,
        display_name=payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    set_auth_cookies(response, user.id)
    return UserPrivate.model_validate(user)


@router.post("/login")
async def login(payload: LoginRequest, db: DbSession, response: Response) -> UserPrivate:
    identifier = payload.identifier.strip().lower()
    column = User.email if "@" in identifier else User.username
    user = await db.scalar(select(User).where(column == identifier))

    if user is None:
        verify_password(payload.password, _DUMMY_HASH)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    set_auth_cookies(response, user.id)
    return UserPrivate.model_validate(user)


@router.post("/refresh")
async def refresh(request: Request, db: DbSession, response: Response) -> UserPrivate:
    token = request.cookies.get(REFRESH_COOKIE)
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    try:
        user_id = decode_token(token, "refresh")
    except TokenError:
        clear_auth_cookies(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from None

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        clear_auth_cookies(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    set_auth_cookies(response, user.id)
    return UserPrivate.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    clear_auth_cookies(response)
