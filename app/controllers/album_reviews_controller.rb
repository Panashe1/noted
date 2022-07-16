class AlbumReviewsController < ApplicationController
  def show
    @album = MusicAPI.new.findAlbum(params[:id])
    artistid = @album.artists[0].id
    @artist = MusicAPI.new.findArtist(artistid)
    @album_review = AlbumReview.new
    @reviews = AlbumReview.where("api_id LIKE ?", "%#{params[:id]}%")
  end

  def create
    @album_review = AlbumReview.new(review_params)
    @album = MusicAPI.new.findAlbum(params[:id])
    albumid = @album_review.api_id
    if @album_review.save
      redirect_to album_review_path(albumid)
    else
      render :show
    end
  end

  def review_params
    params.require(:album_review).permit(:description, :rating, :api_id, :user_id, :name)
  end
end
