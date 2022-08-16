class RegistrationsController < Devise::RegistrationsController
  protected
    def after_update_path_for(resource)
      users_path(resource)
    end
end
