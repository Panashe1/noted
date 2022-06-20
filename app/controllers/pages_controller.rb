class PagesController < ApplicationController

  def home
  end

  def show_search_results
    @artists = RSpotify::Artist.search(params[:searchText])

  end
end
