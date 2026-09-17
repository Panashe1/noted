from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.user import User
from app.schemas.user import UserPrivate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def read_me(user: CurrentUser) -> UserPrivate:
    return UserPrivate.model_validate(user)


@router.get("/{username}")
async def read_user(username: str, db: DbSession) -> UserPublic:
    user = await db.scalar(select(User).where(User.username == username.lower()))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserPublic.model_validate(user)
