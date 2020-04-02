import pandas as pd 
import csv
from io import StringIO
from d00_utils.upsert_pandas_df import clean_df_db_dups


primary_key_cols = {"artists": ['artist_id'],
                    "listeners": ['listener_id'],
                    "tracks": ['track_id'], 
                    "albums": ['album_id'], 
                    "genre": ['genre_name'], 
                    "topartists": ['listener_id', 'artist_id', 'time_span'],
                    "toptracks": ['listener_id', 'track_id', 'time_span'],
                    'createdby': ['track_id', 'artist_id'],
                    'albumcontainstrack': ['album_id', 'track_id'],
                    'artisthasgenre': ['genre_name', 'artist_id'], 
                    'albumhasgenre': ['genre_name', 'album_id']
                    }

def insert_new_user_to_database(new_user_data:dict, db_engine):
    """
    Inserts a new user's spotify info to the database
    Todo: Ensure that we are not inserting duplicate data to the databse
    (will cause a failure)
    """
    df_table_mapping = [('user_info', 'listeners'),
                        # user top track info
                        ('top_tracks_to_add', 'tracks'), 
                        ('user_top_tracks', 'toptracks'), 
                        # top track artist info
                        ('top_track_artists_to_add', 'artists'),
                        ('top_track_created_by', 'createdby'),
                        ('top_track_genres_to_add', 'genre'),
                        ('top_track_artists_genres', 'artisthasgenre'),
                        # top track album info
                        ('top_tracks_albums_to_add', 'albums'),
                        ('album_contains_track', 'albumcontainstrack'),
                        ('top_tracks_album_genres_to_add', 'genre'),
                        ('top_tracks_album_genres', 'albumhasgenre'),
                        # top artists
                        ('top_artists_to_add', 'artists'),
                        ('user_top_artists', 'topartists'),
                        ('top_artists_genres_to_add', 'genre'),
                        ('top_artists_genres', 'artisthasgenre')
                        ]
    conn = db_engine.raw_connection()
    cursor = conn.cursor()

    for df_name, table_name in df_table_mapping:
        df = new_user_data[df_name]
        #remove dups before insertion
        df = clean_df_db_dups(df=df, 
                              tablename=table_name, 
                              engine=db_engine, 
                              dup_cols=primary_key_cols[table_name])

        output = StringIO()
        df.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0)
        contents = output.getvalue()
        # null values become ''
        cursor.copy_from(output, table_name, null="")
        conn.commit()

        # new_user_data[df_name].to_sql(name=table_name, 
        #                       con=db_connection, 
        #                       if_exists='append',
        #                       index=False,
        #                       method=psql_upsert)
    return 

