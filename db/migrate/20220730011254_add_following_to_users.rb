class AddFollowingToUsers < ActiveRecord::Migration[6.1]
  def change
    add_column :users, :following, :integer, array: true, default: []
  end
end
