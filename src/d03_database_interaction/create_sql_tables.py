from d00_utils.load_confs import load_credentials, load_paths
from d00_utils.data_loader_sql import DataLoaderSQL


def create_sql_tables(drop=False):

    paths = load_paths()

    # create queries
    drop_commands = None
    if drop:
        drop_commands = [
            "DROP TABLE artists, \
                        listeners, \
                        tracks, \
                        albums, \
                        genre, \
                        topartists, \
                        toptracks, \
                        createdby, \
                        albumcontainstrack, \
                        artisthasgenre, \
                        albumhasgenre \
                        CASCADE;"
        ]

    commands = [
    """
    CREATE TABLE artists
    (artist_id VARCHAR(200) NOT NULL PRIMARY KEY ,
     artist_name VARCHAR(200) NOT NULL,
     artist_pop INTEGER NOT NULL,
     num_followers INTEGER NOT NULL,
     artist_image_url VARCHAR(400) NOT NULL)
    """,

    """
    CREATE TABLE listeners
    (listener_id VARCHAR(200) NOT NULL PRIMARY KEY,
     display_name VARCHAR(200) NOT NULL,
     username VARCHAR(200) NOT NULL,
     access_token VARCHAR(200) NOT NULL, 
     expires_in INTEGER NOT NULL,  
     refresh_token VARCHAR(200) NOT NULL, 
     scope VARCHAR(200) NOT NULL,
     num_followers INTEGER NOT NULL,
     listener_image_url VARCHAR(400) NOT NULL
    )
    """,

    """
    CREATE TABLE tracks
    (track_id VARCHAR(200) NOT NULL PRIMARY KEY,
     track_name VARCHAR(200) NOT NULL,
     track_pop INTEGER NOT NULL,
     preview_url VARCHAR(400) NOT NULL,
     acousticness NUMERIC,
     danceability NUMERIC,
     energy NUMERIC,
     valence  NUMERIC,
     loudness NUMERIC,
     tempo  NUMERIC,
     instrumentalness NUMERIC,
     speechiness NUMERIC,
     mode INTEGER,
     time_signature INTEGER,
     liveness NUMERIC
    )
    """,

    """
    CREATE TABLE albums
    (album_id VARCHAR(200) NOT NULL PRIMARY KEY,
     album_type VARCHAR(200) NOT NULL,
     album_name VARCHAR(200) NOT NULL,
     album_release_date timestamp NOT NULL,
     album_image_url VARCHAR(400) NOT NULL
    )
    """,
    
    """
    CREATE TABLE genre(
     genre_name VARCHAR(200) NOT NULL PRIMARY KEY
    )
    """,

    """
    CREATE TABLE topartists
    (listener_id VARCHAR(200) NOT NULL ,
     artist_id VARCHAR(200) NOT NULL,
     time_span VARCHAR(200) NOT NULL ,
     PRIMARY KEY(listener_id, artist_id, time_span),
     CONSTRAINT listenerid_fkey FOREIGN KEY (listener_id)
     REFERENCES listeners(listener_id),
     CONSTRAINT artistid_fkey FOREIGN KEY (artist_id)
     REFERENCES artists(artist_id)
    )
    """,

    """
    CREATE TABLE toptracks
    (listener_id VARCHAR(200) NOT NULL ,
    track_id VARCHAR(200) NOT NULL ,
    time_span VARCHAR(200) NOT NULL, 
    PRIMARY KEY(listener_id, track_id, time_span),
    CONSTRAINT listenerid_fkey FOREIGN KEY (listener_id)
    REFERENCES listeners(listener_id),
    CONSTRAINT trackid_fkey FOREIGN KEY (track_id)
    REFERENCES tracks(track_id)
    )
    """,

    """
    CREATE TABLE createdby
    (track_id VARCHAR(200) NOT NULL ,
     artist_id VARCHAR(200) NOT NULL,
    PRIMARY KEY(track_id,artist_id),
    CONSTRAINT trackid_fkey FOREIGN KEY (track_id)
    REFERENCES tracks(track_id),
    CONSTRAINT artistid_fkey FOREIGN KEY (artist_id)
    REFERENCES artists(artist_id)
    )
    """,

    """
    CREATE TABLE albumcontainstrack(
    album_id VARCHAR(200) NOT NULL,
    track_id VARCHAR(200) NOT NULL,
    PRIMARY KEY(album_id,track_id),
    CONSTRAINT albumid_fkey FOREIGN KEY (album_id)
    REFERENCES albums(album_id),
    CONSTRAINT track_id FOREIGN KEY (track_id)
    REFERENCES tracks(track_id)
    )
    """, 

    """
    CREATE TABLE artisthasgenre(
    artist_id VARCHAR(200) NOT NULL, 
    genre_name VARCHAR(200) NOT NULL,
    PRIMARY KEY(genre_name,artist_id),
    CONSTRAINT artistid_fkey FOREIGN KEY (artist_id)
    REFERENCES artists(artist_id),
    CONSTRAINT genre_fkey FOREIGN KEY (genre_name)
    REFERENCES genre(genre_name)
    )
    """,

    """
    CREATE TABLE albumhasgenre(
    album_id VARCHAR(200) NOT NULL, 
    genre_name VARCHAR(400) NOT NULL,
    PRIMARY KEY(genre_name,album_id),
    CONSTRAINT albumid_fkey FOREIGN KEY (album_id)
    REFERENCES albums(album_id),
    CONSTRAINT genre_fkey FOREIGN KEY (genre_name)
    REFERENCES genre(genre_name)
    )
    """
    ]

    # execute queries
    dl = DataLoaderSQL(creds=load_credentials(), paths=paths)

    if drop_commands is not None:
        for command in drop_commands:
            dl.execute_raw_sql_query(sql=command)

    for command in commands:
        dl.execute_raw_sql_query(sql=command)
