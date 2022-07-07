def displayArtist(searchTerm)
  @artists = RSpotify::Artist.search(searchTerm)
  return @artists
end

def displayAlbums(artistId)
  @albums = RSpotify::Album.search(searchTerm)
  return @albums
end

def randomRecommendations()
  @random = RSpotify::Recommendations.generate(seed_artists: ['0oSGxfWSnnOXhD2fKuzsmi'], seed_tracks: ['0oSGxfWSnnOXhD2fKuzsmi'])
  return @random
end

def search
end


def getPopularArtists()
end
