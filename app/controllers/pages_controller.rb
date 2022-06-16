class PagesController < ApplicationController
  def home
    @popular = RSpotify::Artist.search('Greenday')
    @friend = RSpotify::Album.search('Cat')
    @trending = RSpotify::Recommendations.generate(seed_genres: ['rock', 'pop'])
  end

  def show_search_results
    @artist = RSpotify::Artist.search(params[:searchText]).first
  end
end
