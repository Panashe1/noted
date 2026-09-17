import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.music import AlbumOut, AlbumSearchResponse
from app.services.music import Catalog

router = APIRouter(prefix="/albums", tags=["albums"])


@router.get("/search")
async def search_albums(
    catalog: Catalog,
    q: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> AlbumSearchResponse:
    query = q.strip()
    albums, source = await catalog.search(query, limit=limit)
    return AlbumSearchResponse(
        query=query,
        source=source,
        results=[AlbumOut.model_validate(album) for album in albums],
    )


@router.get("/apple/{apple_id}")
async def read_album_by_apple_id(apple_id: int, catalog: Catalog) -> AlbumOut:
    album = await catalog.get_by_apple_id(apple_id)
    if album is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Album not found")
    return AlbumOut.model_validate(album)


@router.get("/{album_id}")
async def read_album(album_id: uuid.UUID, catalog: Catalog) -> AlbumOut:
    album = await catalog.get_by_id(album_id)
    if album is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Album not found")
    return AlbumOut.model_validate(album)
