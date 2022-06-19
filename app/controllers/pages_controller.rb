class PagesController < ApplicationController
  def home
  end

  def show_search_results
    @artist = RSpotify::Artist.search(params[:searchText]).first
  end
end
