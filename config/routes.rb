Rails.application.routes.draw do
  devise_for :users
  root 'pages#home'
  get 'users/:id' => 'users#show'
  get 'pages/search/:id/artist' => 'pages#searchArtist', as: 'searchArtist'
  get 'pages/search/:id/album' => 'pages#searchAlbum', as: 'searchAlbum'
  get 'pages/search/:id/track' => 'pages#searchTrack', as: 'searchTrack'



  resources :artists, only: [:index, :show]
  resources :songs do
    resources :song_reviews, only: [:create, :index, :show, :edit, :update, :new]
  end
  resources :song_reviews, only: [:destroy]
  resources :albums do
    resources :albums_reviews, only: [:create, :index, :show, :edit, :update, :new]
  end
  resources :album_reviews, only: [:destroy]
end
