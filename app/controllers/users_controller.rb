class UsersController < ApplicationController
  def show
    @user = User.find(params[:id])
    @album_reviews = AlbumReview.where(user_id: @user.id)
    @count = AlbumReview.where(user_id: @user.id)
    @song_reviews = SongReview.where(user_id: @user.id)
  end
end
