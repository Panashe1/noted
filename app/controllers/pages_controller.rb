class PagesController < ApplicationController
  def home
    @popular = RSpotify::Artist.search('Vance')
    @friend = RSpotify::Album.search('Cat')
    @trending = RSpotify::Recommendations.generate(seed_genres: ['rock', 'pop'])
  end
end
