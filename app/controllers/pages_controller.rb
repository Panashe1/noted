class PagesController < ApplicationController

  def home
    @artists = MusicAPI.new.displayArtist('vance')
  end

  def search
    # Example of find
    @artists = RSpotify::Artist.find('0TCuSgJzNaRyxjbvvLjBK3')
  end
end
