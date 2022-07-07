require_relative '../services/api.rb'

class PagesController < ApplicationController

  def home
    @function = displayArtist('vance', @artists)
  end

  def show_search_results
    @artists = RSpotify::Artist.search(params[:searchText])
  end
end
