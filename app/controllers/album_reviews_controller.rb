class AlbumReviewsController < ApplicationController
  def show
    @album = MusicAPI.new.findAlbum(params[:id])
    artistid = @album.artists[0].id
    @artist = MusicAPI.new.findArtist(artistid)
    @album_review = AlbumReview.new
    @reviews = AlbumReview.where("api_id LIKE ?", "%#{params[:id]}%")
    @tracks = @album.tracks
    @finalsum = rating_score
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

  def rating_score
    sum = 0
    @reviews.each do |review|
      if review.rating
    sum += review&.rating
      end
    end
    @reviews&.count&.zero? ? '0.0' : (sum / @reviews.count.to_f)
  end

  def review_params
    params.require(:album_review).permit(:description, :rating, :api_id, :user_id, :title)
  end
end
