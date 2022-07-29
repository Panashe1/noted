# Class to help manage the use of the spotify API
class MusicAPI
  # return a group of artists based on the search term
  def displayArtist(searchTerm)
    @artists = RSpotify::Artist.search(searchTerm)
    return @artists[0..7]
  end

  # return a single of artist based on the search term
  def findArtist(artistId)
    @artist = RSpotify::Artist.find(artistId)
    return @artist
  end

  # return a group of albums based on the search term
  def displayAlbums(searchTerm)
    @albums = RSpotify::Album.search(searchTerm)
    return @albums[0..7]
  end

  # return a single of album based on the search term
  def findAlbum(albumId)
    @album = RSpotify::Album.find(albumId)
    return @album
  end

  def displayTracks(searchTerm)
    @tracks = RSpotify::Track.search(searchTerm)
    return @tracks
  end

  def findTrack(trackId)
    @track = RSpotify::Track.find(trackId)
    return @track
  end

# return a group of Recommendations based on the the defined below data
  def randomRecommendations()
    @random = RSpotify::Recommendations.generate(seed_artists: ['0oSGxfWSnnOXhD2fKuzsmi'], seed_tracks: ['0oSGxfWSnnOXhD2fKuzsmi'])
    return @random
  end


  def display_more_albums(searchTerm)
    @albums = RSpotify::Album.search(searchTerm)
    return @albums[0..17]
  end

  def display_more_artists(searchTerm)
    @artists = RSpotify::Artist.search(searchTerm)
    return @artists[0..17]
  end

  def display_more_tracks(searchTerm)
    @tracks = RSpotify::Track.search(searchTerm)
    return @tracks[0..17]
  end
end
