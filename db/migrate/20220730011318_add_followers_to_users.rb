class AddFollowersToUsers < ActiveRecord::Migration[6.1]
  def change
    add_column :users, :followers, :integer, array: true, default: []
  end
end
