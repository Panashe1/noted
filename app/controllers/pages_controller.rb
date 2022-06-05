require 'rspotify'

class PagesController < ApplicationController
  def home
    @search = RSpotify::Artist.search('Arctic Monkeys')
  end
end
