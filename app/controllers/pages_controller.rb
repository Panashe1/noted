class PagesController < ApplicationController

  def home
    @artists = MusicAPI.new.displayArtist('ariana')
    @albums = MusicAPI.new.displayAlbums('lil')
    @tracks = MusicAPI.new.displayTracks('bush')
  end

  def searchArtist
    # if general search term is provided, search for artist, album, and track
    if params[:searchText]
      @resultsArtist = MusicAPI.new.findArtist(params[:searchText])

      @top_tracks = @resultsArtist.top_tracks(:US)

      @top_albums = @resultsArtist.albums(limit: 8, country: 'US')

    else
      @resultsArtist = MusicAPI.new.findArtist(params[:id])
      @top_tracks = @resultsArtist.top_tracks(:US)
      @top_albums = @resultsArtist.albums(limit: 8, country: 'US')
    end
  end

  def searchTrack
    @resultsTrack = MusicAPI.new.findTrack(params[:id])
  end
end
