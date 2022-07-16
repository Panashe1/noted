class UsersController < ApplicationController
  def show
    @user = User.find(params[:id])
    @album_reviews = AlbumReview.all
    @count = AlbumReview.where(user_id:current_user.id)
  end
end
