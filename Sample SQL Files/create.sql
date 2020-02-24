
--for postgresSQL MULTIPLE Attribute primary keys and references are all table 
--constraints.

CREATE TABLE artists
(id VARCHAR(200) NOT NULL PRIMARY KEY ,
 artist_name VARCHAR(200) NOT NULL,
 genres VARCHAR(200) NOT NULL,
 pop INTEGER NOT NULL,
 followers INTEGER NOT NULL,
 image_url VARCHAR(400) NOT NULL);

CREATE TABLE listeners
(id VARCHAR(200) NOT NULL PRIMARY KEY,
 display_name VARCHAR(200) NOT NULL,
 followers INTEGER NOT NULL,
 image_url VARCHAR(400) NOT NULL
);

CREATE TABLE tracks
(id VARCHAR(200) NOT NULL PRIMARY KEY,
 track_name VARCHAR(200) NOT NULL,
 pop INTEGER NOT NULL,
 review_url VARCHAR(400) NOT NULL
);

CREATE TABLE albums
(id VARCHAR(200) NOT NULL PRIMARY KEY,
name VARCHAR(200) NOT NULL,
album_type VARCHAR(200) NOT NULL,
image_url VARCHAR(400) NOT NULL
);

CREATE TABLE topartists
(listener_id VARCHAR(200) NOT NULL ,
artist_id VARCHAR(200) NOT NULL,
time_span VARCHAR(200) NOT NULL ,
PRIMARY KEY(listener_id, artist_id, time_span),
CONSTRAINT listenerid_fkey FOREIGN KEY (listener_id)
REFERENCES listeners(id),
CONSTRAINT artistid_fkey FOREIGN KEY (artist_id)
REFERENCES artists(id)
);


CREATE TABLE toptracks
(listener_id VARCHAR(200) NOT NULL ,
track_id VARCHAR(200) NOT NULL ,
time_span VARCHAR(200) NOT NULL, 
PRIMARY KEY(listener_id, track_id, time_span),
CONSTRAINT listenerid_fkey FOREIGN KEY (listener_id)
REFERENCES listeners(id),
CONSTRAINT trackid_fkey FOREIGN KEY (track_id)
REFERENCES tracks(id)
);

CREATE TABLE createdby
(track_id VARCHAR(200) NOT NULL ,
artist_id VARCHAR(200) NOT NULL,
PRIMARY KEY(track_id,artist_id),
CONSTRAINT trackid_fkey FOREIGN KEY (track_id)
REFERENCES tracks(id),
CONSTRAINT artistid_fkey FOREIGN KEY (artist_id)
REFERENCES artists(id)
);


CREATE TABLE albumcontainstrack
(album_id VARCHAR(200) NOT NULL,
artist_id VARCHAR(200) NOT NULL,
PRIMARY KEY(album_id,artist_id),
CONSTRAINT albumid_fkey FOREIGN KEY (album_id)
REFERENCES albums(id),
CONSTRAINT artistid_fkey FOREIGN KEY (artist_id)
REFERENCES artists(id)
);

-- syntax to alter columns.
--ALTER TABLE artists
--  ALTER COLUMN image_url TYPE VARCHAR (500);

