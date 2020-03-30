	
DROP TABLE albumcontainstrack;


CREATE TABLE albumcontainstrack(
album_id VARCHAR(200) NOT NULL,
track_id VARCHAR(200) NOT NULL,
PRIMARY KEY(album_id,track_id),
CONSTRAINT albumid_fkey FOREIGN KEY (album_id)
REFERENCES albums(id),
CONSTRAINT track_id FOREIGN KEY (track_id)
REFERENCES tracks(id));


ALTER TABLE tracks 
ADD COLUMN acousticness NUMERIC;

ALTER TABLE tracks 
ADD COLUMN danceability NUMERIC;

ALTER TABLE tracks 
ADD COLUMN energy NUMERIC;

ALTER TABLE tracks 
ADD COLUMN instrumentalness NUMERIC;

ALTER TABLE tracks 
ADD COLUMN liveness NUMERIC;

ALTER TABLE tracks 
ADD COLUMN loudness NUMERIC;

ALTER TABLE tracks 
ADD COLUMN mode INTEGER;

ALTER TABLE tracks 
ADD COLUMN speechiness  NUMERIC;

ALTER TABLE tracks 
ADD COLUMN tempo  NUMERIC;

ALTER TABLE tracks 
ADD COLUMN time_sig INTEGER;

ALTER TABLE tracks 
ADD COLUMN valence  NUMERIC;






CREATE TABLE genre(
    genre_name VARCHAR(200) NOT NULL PRIMARY KEY
);



CREATE TABLE artisthasgenre(
    genre_name VARCHAR(200) NOT NULL,
    artist_id VARCHAR(200) NOT NULL, 
    PRIMARY KEY(genre_name,artist_id),
    CONSTRAINT artistid_fkey FOREIGN KEY (artist_id)
    REFERENCES artists(id),
    CONSTRAINT genre_fkey FOREIGN KEY (genre_name)
    REFERENCES genre(genre_name)
);


CREATE TABLE albumhasgenre(
    genre_name VARCHAR(400) NOT NULL,
    album_id VARCHAR(200) NOT NULL, 
    PRIMARY KEY(genre_name,album_id),
    CONSTRAINT albumid_fkey FOREIGN KEY (album_id)
    REFERENCES albums(id),
    CONSTRAINT genre_fkey FOREIGN KEY (genre_name)
    REFERENCES genre(genre_name)

);

-- all of the above have been implemented.