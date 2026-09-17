from datetime import date

from app.services.music.itunes import parse_album, upscale_artwork

SAMPLE = {
    "wrapperType": "collection",
    "collectionType": "Album",
    "collectionId": 1109714933,
    "collectionName": "In Rainbows",
    "artistId": 657515,
    "artistName": "Radiohead",
    "artworkUrl100": "https://is1-ssl.mzstatic.com/image/thumb/x/100x100bb.jpg",
    "releaseDate": "2007-10-10T07:00:00Z",
    "primaryGenreName": "Alternative",
    "trackCount": 10,
}


def test_parse_album_maps_fields() -> None:
    album = parse_album(SAMPLE)
    assert album is not None
    assert album.provider_id == 1109714933
    assert album.title == "In Rainbows"
    assert album.artist.name == "Radiohead"
    assert album.artist.provider_id == 657515
    assert album.release_date == date(2007, 10, 10)
    assert album.artwork_url is not None and "600x600bb" in album.artwork_url


def test_parse_album_ignores_tracks_and_singles() -> None:
    assert parse_album({**SAMPLE, "wrapperType": "track"}) is None
    assert parse_album({**SAMPLE, "collectionType": "Single"}) is None


def test_parse_album_tolerates_missing_artist_id() -> None:
    album = parse_album({k: v for k, v in SAMPLE.items() if k != "artistId"})
    assert album is not None
    assert album.artist.provider_id is None


def test_upscale_artwork() -> None:
    assert upscale_artwork(None) is None
    assert upscale_artwork("https://x/100x100bb.jpg", 1000) == "https://x/1000x1000bb.jpg"
