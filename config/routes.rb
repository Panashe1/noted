Rails.application.routes.draw do
  root 'pages#home'
  get 'search', to: 'pages#show_search_results'
  devise_for :users
end
