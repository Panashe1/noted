class CreateSongReviews < ActiveRecord::Migration[6.1]
  def change
    create_table :song_reviews do |t|
      t.references :user, null: false, foreign_key: true
      t.string :title
      t.text :description
      t.integer :likes
      t.string :api_id
      t.float :rating

      t.timestamps
    end
  end
end
