import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ArtistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    apple_id: int | None


class AlbumOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    artist: ArtistOut
    apple_id: int | None
    upc: str | None
    release_date: date | None
    artwork_url: str | None
    genre: str | None
    track_count: int | None


SearchSource = Literal["local", "itunes", "mixed"]


class AlbumSearchResponse(BaseModel):
    query: str
    source: SearchSource
    results: list[AlbumOut]
