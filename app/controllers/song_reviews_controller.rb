class SongReviewsController < ApplicationController
  def show
    @song = MusicAPI.new.findTrack(params[:id])
    album_id = @song.album.id
    @album = MusicAPI.new.findAlbum(album_id)
    @song_review = SongReview.new
    @reviews = SongReview.where("api_id LIKE ?", "%#{params[:id]}%")
    @tracks = @album.tracks
  end

  def create
    @song_review = SongReview.new(review_params)
    @song = MusicAPI.new.findTrack(params[:id])
    songid = @song_review.api_id
    if @song_review.save
      redirect_to song_review_path(songid)
    else
      render :show
    end
  end

  def review_params
    params.require(:song_review).permit(:description, :rating, :api_id, :user_id, :title)
  end
end
