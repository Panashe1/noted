import uuid
from datetime import date, datetime
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.music import AlbumOut
from app.schemas.user import UserPublic

# The API speaks in stars; the database stores half-stars. Values in 0.5 steps are exact
# in binary floating point, so `multiple_of` is reliable here.
Rating = Annotated[float, Field(ge=0.5, le=5.0, multiple_of=0.5)]

BODY_MAX_LENGTH = 10_000


def to_half_stars(rating: float) -> int:
    return round(rating * 2)


class ReviewWrite(BaseModel):
    """Payload for creating or replacing your review of an album."""

    rating: Rating
    body: str | None = Field(default=None, max_length=BODY_MAX_LENGTH)
    listened_at: date | None = None
    contains_spoilers: bool = False

    @field_validator("body")
    @classmethod
    def _empty_body_is_null(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @model_validator(mode="after")
    def _listened_at_is_not_in_the_future(self) -> Self:
        if self.listened_at is not None and self.listened_at > date.today():
            raise ValueError("listened_at cannot be in the future")
        return self


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user: UserPublic
    rating: float
    body: str | None
    listened_at: date | None
    contains_spoilers: bool
    created_at: datetime
    updated_at: datetime


class ReviewWithAlbum(ReviewOut):
    album: AlbumOut


class ReviewPage(BaseModel):
    items: list[ReviewOut]
    total: int
    limit: int
    offset: int


class ReviewWithAlbumPage(BaseModel):
    items: list[ReviewWithAlbum]
    total: int
    limit: int
    offset: int
