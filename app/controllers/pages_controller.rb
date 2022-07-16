class PagesController < ApplicationController

  def home
    @artists = MusicAPI.new.displayArtist('vance')
    @albums = MusicAPI.new.displayAlbums('lil')
    @tracks = MusicAPI.new.displayTracks('bush')
  end

  def searchArtist
    # if general search term is provided, search for artist, album, and track
    if params[:searchText]
      @resultsArtist = MusicAPI.new.findArtist(params[:searchText])
    else
      @resultsArtist = MusicAPI.new.findArtist(params[:id])
      @top_tracks = @resultsArtist.top_tracks(:US).first(4)
    end
  end

  def searchTrack
    @resultsTrack = MusicAPI.new.findTrack(params[:id])
  end

  def resultsPage

  end
end
