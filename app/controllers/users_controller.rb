class UsersController < ApplicationController
  def show
    @user = User.find(params[:id])
    @album_reviews = AlbumReview.where(user_id: @user.id)
    @song_reviews = SongReview.where(user_id: @user.id)
  end

  def community
    @user = User.all
  end

  def follow
    @user = User.find(params[:id])
    userid = @user.id
    current_user.following.push(userid)
    @user.followers.push(current_user.id)
    @user.save
    current_user.save
    redirect_to users_path(@user)
  end


  def unfollow
    @user = User.find(params[:id])
    userid = @user.id
    current_user.following.delete(userid)
    @user.followers.delete(current_user.id)
    @user.save
    current_user.save
    redirect_to users_path(@user)
  end




end
