import uuid
from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.music import Album
from app.models.user import User

MIN_HALF_STARS = 1
MAX_HALF_STARS = 10


class Review(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One user's take on one album.

    A user has at most one review per album, enforced by a unique constraint. Logging the
    same album more than once (Letterboxd's diary/relisten idea) would relax that, and is
    deliberately left to a later milestone.
    """

    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "album_id", name="uq_reviews_user_id_album_id"),
        CheckConstraint(
            f"rating_half_stars BETWEEN {MIN_HALF_STARS} AND {MAX_HALF_STARS}",
            name="rating_half_stars_range",
        ),
        # Both listing paths read newest-first, so carry the sort in the index.
        Index("ix_reviews_album_id_created_at", "album_id", text("created_at DESC")),
        Index("ix_reviews_user_id_created_at", "user_id", text("created_at DESC")),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    album_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("albums.id", ondelete="CASCADE"))
    # Half-stars 1..10 == 0.5..5.0 stars. An integer stays exact on both Postgres and the
    # SQLite the tests run on, and makes AVG() straightforward.
    rating_half_stars: Mapped[int] = mapped_column(SmallInteger)
    body: Mapped[str | None] = mapped_column(Text)
    listened_at: Mapped[date | None] = mapped_column(Date)
    contains_spoilers: Mapped[bool] = mapped_column(default=False, server_default=text("false"))

    # Eagerly joined: these are serialized with every review, and a lazy load inside async
    # request handling would raise rather than quietly issue another query.
    user: Mapped[User] = relationship(lazy="joined")
    album: Mapped[Album] = relationship(lazy="joined")

    @property
    def rating(self) -> float:
        """The stored half-stars as the 0.5-5.0 value the API speaks in."""
        return self.rating_half_stars / 2
