class CreateAlbums < ActiveRecord::Migration[6.1]
  def change
    create_table :albums do |t|
      t.float :average_rating
      t.string :album_id
      t.string :artist_id

      t.timestamps
    end
  end
end
