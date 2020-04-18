import pandas as pd 
import csv
from io import StringIO
import psycopg2

from d00_utils.upsert_pandas_df import clean_df_db_dups

#specify the primary key columns of database 
# TODO: put this in params 
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
        if new_user_data[df_name].empty: 
             continue
        df = new_user_data[df_name]
        #remove dups before insertion
        df = clean_df_db_dups(df=df, 
                              tablename=table_name, 
                              engine=db_engine, 
                              dup_cols=primary_key_cols[table_name])
        # bulk insert df to database 
        copy_df_to_db(df=df, table_name=table_name, conn=conn, cursor=cursor)

    return 


def copy_df_to_db(df, table_name, conn, cursor):
    """
    Given pandas dataframe, raw database connection, and cursor, 
    performs builk insert into database 
    """

    # print()
    # print("============================================")
    # print()
    # print(df)
    # for item in df:
    #     print("   ", df[item])
    #     print()
    # print(table_name)
    # print(conn)
    # print(cursor)
    # print()
    # print("============================================")
    # print()

    output = StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    # null values become ''
    cursor.copy_from(output, table_name, null="")
    conn.commit()


def select_from_table(sql, db_engine): 
    """
    execute select type sql command on db and 
    returns pandas dataframe 
    """ 
    conn = db_engine.raw_connection()
    cursor = conn.cursor()

    results = None
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        col_names = list(map(lambda x: x[0], cursor.description))
        results = pd.DataFrame(results, columns=col_names)
        conn.commit()
    except(Exception, psycopg2.errors.UndefinedTable) as error:
        results = None
        print('Table does not exist. Please create first. Here is the full error message:')
        print(error)
        conn.rollback()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
        conn.rollback()
    finally:
        cursor.close()
        if conn:
            conn.close()

    return results

