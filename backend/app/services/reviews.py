"""Query helpers for reviews and the rating aggregates shown on album pages."""

import uuid
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.models.review import Review


@dataclass(frozen=True, slots=True)
class AlbumStats:
    average_rating: float | None
    review_count: int


async def album_stats(db: AsyncSession, album_id: uuid.UUID) -> AlbumStats:
    row = (
        await db.execute(
            select(func.avg(Review.rating_half_stars), func.count(Review.id)).where(
                Review.album_id == album_id
            )
        )
    ).one()
    average_half_stars, count = row
    if average_half_stars is None:
        return AlbumStats(average_rating=None, review_count=0)
    return AlbumStats(average_rating=round(float(average_half_stars) / 2, 2), review_count=count)


async def load_review(db: AsyncSession, review_id: uuid.UUID) -> Review | None:
    """Re-select a review so its joined `user` and `album` are populated.

    `Session.get` and a freshly added object both leave those relationships unloaded, and
    touching one during serialization would raise in async code.
    """
    review: Review | None = await db.scalar(select(Review).where(Review.id == review_id))
    return review


async def own_review(db: AsyncSession, user_id: uuid.UUID, album_id: uuid.UUID) -> Review | None:
    review: Review | None = await db.scalar(
        select(Review).where(Review.user_id == user_id, Review.album_id == album_id)
    )
    return review


async def list_reviews(
    db: AsyncSession,
    *conditions: ColumnElement[bool],
    limit: int,
    offset: int,
) -> tuple[list[Review], int]:
    """Newest-first page of reviews matching `conditions`, plus the unpaginated total."""
    total = await db.scalar(select(func.count(Review.id)).where(*conditions))
    rows = await db.scalars(
        select(Review)
        .where(*conditions)
        # id breaks ties so paging stays stable when two reviews share a timestamp.
        .order_by(Review.created_at.desc(), Review.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(rows.unique().all()), total or 0
