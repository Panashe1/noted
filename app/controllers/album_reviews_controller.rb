class AlbumReviewsController < ApplicationController
  def show
      @album = MusicAPI.new.findAlbum('7mgdTKTCdfnLoa1HXHvLYM')
      artistid = @album.artists[0].id
      @artist = MusicAPI.new.findArtist(artistid)
      @album_review = AlbumReview.new
  end
end
