import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.deps import CurrentUser, DbSession
from app.models.music import Album
from app.models.review import Review
from app.models.user import User
from app.schemas.review import (
    ReviewOut,
    ReviewPage,
    ReviewWithAlbum,
    ReviewWithAlbumPage,
    ReviewWrite,
    to_half_stars,
)
from app.services.reviews import list_reviews, load_review, own_review

router = APIRouter(tags=["reviews"])

Limit = Annotated[int, Query(ge=1, le=50)]
Offset = Annotated[int, Query(ge=0)]


async def ensure_album_exists(db: DbSession, album_id: uuid.UUID) -> None:
    """404 rather than a foreign-key error when a review targets an unknown album."""
    if await db.get(Album, album_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Album not found")


def _apply(review: Review, payload: ReviewWrite) -> None:
    review.rating_half_stars = to_half_stars(payload.rating)
    review.body = payload.body
    review.listened_at = payload.listened_at
    review.contains_spoilers = payload.contains_spoilers


@router.get("/albums/{album_id}/reviews")
async def list_album_reviews(
    album_id: uuid.UUID, db: DbSession, limit: Limit = 20, offset: Offset = 0
) -> ReviewPage:
    await ensure_album_exists(db, album_id)
    items, total = await list_reviews(db, Review.album_id == album_id, limit=limit, offset=offset)
    return ReviewPage(
        items=[ReviewOut.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/albums/{album_id}/review")
async def read_own_review(album_id: uuid.UUID, db: DbSession, user: CurrentUser) -> ReviewOut:
    review = await own_review(db, user.id, album_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="You have not reviewed this album")
    return ReviewOut.model_validate(review)


@router.put("/albums/{album_id}/review")
async def upsert_own_review(
    album_id: uuid.UUID,
    payload: ReviewWrite,
    db: DbSession,
    user: CurrentUser,
    response: Response,
) -> ReviewOut:
    """Create or replace the caller's review of this album.

    One review per user per album, so this is an upsert rather than a plain POST.
    """
    await ensure_album_exists(db, album_id)

    review = await own_review(db, user.id, album_id)
    created = review is None
    if review is None:
        review = Review(user_id=user.id, album_id=album_id)
        _apply(review, payload)
        db.add(review)
        try:
            await db.commit()
        except IntegrityError:
            # Another request for this same user/album landed first; fall back to updating it.
            await db.rollback()
            existing = await own_review(db, user.id, album_id)
            if existing is None:
                raise
            review, created = existing, False
            _apply(review, payload)
            await db.commit()
    else:
        _apply(review, payload)
        await db.commit()

    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    saved = await load_review(db, review.id)
    assert saved is not None  # noqa: S101 - just committed in this transaction
    return ReviewOut.model_validate(saved)


@router.delete("/albums/{album_id}/review", status_code=status.HTTP_204_NO_CONTENT)
async def delete_own_review(album_id: uuid.UUID, db: DbSession, user: CurrentUser) -> None:
    review = await own_review(db, user.id, album_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="You have not reviewed this album")
    await db.delete(review)
    await db.commit()


@router.get("/reviews/{review_id}")
async def read_review(review_id: uuid.UUID, db: DbSession) -> ReviewWithAlbum:
    review = await load_review(db, review_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Review not found")
    return ReviewWithAlbum.model_validate(review)


@router.get("/users/{username}/reviews")
async def list_user_reviews(
    username: str, db: DbSession, limit: Limit = 20, offset: Offset = 0
) -> ReviewWithAlbumPage:
    user = await db.scalar(select(User).where(User.username == username.lower()))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    items, total = await list_reviews(db, Review.user_id == user.id, limit=limit, offset=offset)
    return ReviewWithAlbumPage(
        items=[ReviewWithAlbum.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
