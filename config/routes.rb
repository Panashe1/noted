Rails.application.routes.draw do
  root 'pages#home'
  get 'pages/search'
  devise_for :users

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
