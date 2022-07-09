class PagesController < ApplicationController

  def home
    @artists = MusicAPI.new.displayArtist('vance')
    @albums = MusicAPI.new.displayAlbums('lil')
    @tracks = MusicAPI.new.displayTracks('bush')
  end

  def search
    # if general search term is provided, search for artist, album, and track
    if params[:search]
      # DO GENERAL SEARCH
    else
      @results = MusicAPI.new.findArtist(params[:id])
    end
  end
end
