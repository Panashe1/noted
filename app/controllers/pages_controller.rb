class PagesController < ApplicationController

  def home
    @artists = MusicAPI.new.displayArtist('vance')
    @albums = MusicAPI.new.displayAlbums('lil')
    @tracks = MusicAPI.new.displayTracks('bush')
  end

  def searchArtist
    # if general search term is provided, search for artist, album, and track
    if params[:search]
      # DO GENERAL SEARCH
    else
      @resultsArtist = MusicAPI.new.findArtist(params[:id])
    end
  end

  def searchAlbum
    @resultsAlbum = MusicAPI.new.findAlbum(params[:id])
  end

  def searchTrack
    @resultsTrack = MusicAPI.new.findTrack(params[:id])
  end
end
