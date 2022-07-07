require_relative '../services/api.rb'

class PagesController < ApplicationController

  def home
    # @function = displayArtist('vance')
    @albums = displayAlbums('vance')
  end

  def search
    # Example of find
    @artists = RSpotify::Artist.find('0TCuSgJzNaRyxjbvvLjBK3')
  end
end
