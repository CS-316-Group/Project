
ALTER TABLE albumcontainstrack
RENAME COLUMN artist_id TO track_id;

ALTER TABLE albumcontainstrack
DROP CONSTRAINT artistid_fkey;

ALTER TABLE albumcontainstrack 
ALTER COLUMN track_id SET CONSTRAINT track_id FOREIGN KEY (track_id)
REFERENCES tracks(id));


ALTER TABLE tracks 
ADD COLUMN acousticness TYPE VARCHAR (500);

ALTER TABLE tracks 
ADD COLUMN danceability TYPE VARCHAR (500);

ALTER TABLE tracks 
ADD COLUMN energy TYPE VARCHAR (500);

ALTER TABLE tracks 
ADD COLUMN valence TYPE VARCHAR (500);

ALTER TABLE tracks 
ADD COLUMN loudness TYPE VARCHAR (500);

ALTER TABLE tracks 
ADD COLUMN tempo TYPE VARCHAR (500);

ALTER TABLE tracks 
ADD COLUMN instrumentalness TYPE VARCHAR (500);

ALTER TABLE tracks 
ADD COLUMN speechiness TYPE VARCHAR (500);

ALTER TABLE tracks 
ADD COLUMN mode TYPE VARCHAR (500);

ALTER TABLE tracks 
ADD COLUMN time_sig TYPE VARCHAR (500);

CREATE TABLE genre(
    genre_name VARCHAR(400) NOT NULL PRIMARY KEY
);



CREATE TABLE artisthasgenre(
    genre_name VARCHAR(400) NOT NULL,
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

