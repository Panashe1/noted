class UsersController < ApplicationController
  def show
    @user = User.find(params[:id])
    @album_reviews = AlbumReview.all
  end


end
