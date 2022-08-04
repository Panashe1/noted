Rails.application.routes.draw do
  devise_for :users, :controllers => { :registrations => :registrations }
  root 'pages#home'
  get 'users/community' => 'users#community', as: 'community'
  get 'users/:id' => 'users#show', as: 'users'

  post 'users/:id/follow' => 'users#follow', as: 'follow'
  post 'users/:id/unfollow' => 'users#unfollow', as: 'unfollow'
  get 'pages/search/:id/artist' => 'pages#searchArtist', as: 'searchArtist'
  get 'pages/search/:id/album' => 'pages#searchAlbum', as: 'searchAlbum'
  get 'pages/search/:id/track' => 'pages#searchTrack', as: 'searchTrack'
  get 'pages/results' => 'pages#resultsPage', as: 'results'

  resources :song_reviews, only: [:create, :index, :show, :edit, :update, :new]
  resources :album_reviews, only: [:create, :index, :show, :edit, :update, :new]
  resources :song_reviews, only: [:destroy]
  resources :album_reviews, only: [:destroy]
end
