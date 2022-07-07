class CreateSongs < ActiveRecord::Migration[6.1]
  def change
    create_table :songs do |t|
      t.float :average_rating
      t.string :song_id
      t.string :album_id

      t.timestamps
    end
  end
end
