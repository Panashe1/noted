class CreateSongReviews < ActiveRecord::Migration[6.1]
  def change
    create_table :song_reviews do |t|
      t.references :user, null: false, foreign_key: true
      t.string :title
      t.text :description
      t.integer :likes
      t.string :song_id
      t.integer :rating

      t.timestamps
    end
  end
end
