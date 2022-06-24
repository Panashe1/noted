class PagesController < ApplicationController

  def home
    @artists = RSpotify::Artist.search("vance")
  end

  def show_search_results
    @artists = RSpotify::Artist.search(params[:searchText])

  end
end
