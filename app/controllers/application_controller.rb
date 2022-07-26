class ApplicationController < ActionController::Base
  before_action :configure_permitted_parameters, if: :devise_controller?
  RSpotify.authenticate(ENV['spotify_client_id'], ENV['spotify_secret_key'])

  include Pundit::Authorization

  # Pundit: white-list approach.
  after_action :verify_authorized, except: :index, unless: :skip_pundit?
  after_action :verify_policy_scoped, only: :index, unless: :skip_pundit?

  rescue_from Pundit::NotAuthorizedError, with: :user_not_authorized
  def user_not_authorized
    flash[:alert] = 'You are not authorized to perform this action.'
    redirect_to(root_path)
  end
  # STEPS TO ENABLE AUTH IN A CONTROLLER
  # Add to controllers code to fix authorize error
  # authorize @instance_variable_name
  # Create Policy
  # rails g pundit:policy NAME ie restuarant
  # Edit Policy
  # inside the new polciy.rb create a function
  # Use if Statement in View
  # if policy() .....

  private

  # =~ /(^(rails_)?admin)|(^pages$)/

  def skip_pundit?
    devise_controller? || params[:controller]
    # Temp turned off until project week where it will be decided by team if we would like to implement
  end

  def configure_permitted_parameters
    # For additional fields in app/views/devise/registrations/new.html.erb
    devise_parameter_sanitizer.permit(:sign_up, keys: [:first_name, :last_name, :photo])

    # For additional in app/views/devise/registrations/edit.html.erb
    devise_parameter_sanitizer.permit(:account_update, keys: [:first_name, :last_name, :photo])
  end
end
