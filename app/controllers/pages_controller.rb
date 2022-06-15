class PagesController < ApplicationController
  def home
    @search = RSpotify::Artist.search('Greenday')
  end
end
