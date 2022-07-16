class AlbumReviewsController < ApplicationController
  def show
      @album = MusicAPI.new.findAlbum(params[:id])
      artistid = @album.artists[0].id
      @artist = MusicAPI.new.findArtist(artistid)
      @album_review = AlbumReview.new
  end

  def create
    @album_review = AlbumReview.new(review_params)
    @album = MusicAPI.new.findAlbum(params[:id])
    @album_review.api_id = @album.id
    @album_review.user_id = current_user.id
    if @album_review.save
      redirect_to show
    else
      render :show
    end
  end

  def review_params
    params.require(:album_review).permit(:description, :rating)
  end
end
