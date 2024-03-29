class PagesController < ApplicationController

  def home
    @artists1 = MusicAPI.new.displayArtist('bee gee')
    @artists2 = MusicAPI.new.displayArtist('arianna')
    @artists3 = MusicAPI.new.displayArtist('vance')
    @artists4 = MusicAPI.new.displayArtist('kate bush')
    @artists5 = MusicAPI.new.displayArtist('Beyoncé')
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

  def resultsPage
    @query = params[:searchText]['query'];
    @results_artist = MusicAPI.new.displayArtist(params[:searchText]['query']);
    @results_album = MusicAPI.new.displayAlbums(params[:searchText]['query']);

    @results_more_artists = MusicAPI.new.display_more_artists(params[:searchText]['query']);
    @results_more_albums = MusicAPI.new.display_more_albums(params[:searchText]['query']);
    @results_more_tracks = MusicAPI.new.display_more_tracks(params[:searchText]['query']);
  end

  def contact
  end
end
