import uuid
from datetime import date

from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Artist(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "artists"
    __table_args__ = (
        Index(
            "ix_artists_name_trgm",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    name: Mapped[str] = mapped_column(String(255), index=True)
    apple_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)

    albums: Mapped[list["Album"]] = relationship(back_populates="artist")


class Album(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "albums"
    __table_args__ = (
        Index(
            "ix_albums_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
    )

    title: Mapped[str] = mapped_column(String(255), index=True)
    artist_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("artists.id", ondelete="RESTRICT"), index=True
    )
    # Provider identity. apple_id is the iTunes/Apple Music collectionId; upc is the
    # industry barcode. Both nullable so albums can come from other sources later.
    apple_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    upc: Mapped[str | None] = mapped_column(String(32), unique=True)
    release_date: Mapped[date | None]
    artwork_url: Mapped[str | None] = mapped_column(String(500))
    genre: Mapped[str | None] = mapped_column(String(100))
    track_count: Mapped[int | None]

    # Eager-load the artist so serializing an Album never triggers a lazy load in async code.
    artist: Mapped[Artist] = relationship(back_populates="albums", lazy="joined")
