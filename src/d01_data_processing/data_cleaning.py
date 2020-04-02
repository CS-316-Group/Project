import pandas as pd
import numpy as np
from pandas.io.json import json_normalize

from d00_utils.explode import explode
from d01_data_processing.spotify_user import SpotifyUser


# TODO: remove drop duplicates for efficiency since we already check that in the app
def clean_listener_info(new_user:SpotifyUser):
    """
    """
    listener_username = new_user.username
    listener_info = json_normalize(new_user.info())

    if (len(listener_info['images'][0]) > 0):
        profile_pic_url = listener_info['images'][0][0]['url']
    else:
        profile_pic_url = 'NULL'

    user_type = listener_info['type'][0]
    assert user_type == 'user', f'Individual type must be user, instead is {user_type}'
    listener_info = (listener_info.drop(['href', 'images', 'uri', 
                                         'external_urls.spotify', 
                                         'type', 'followers.href'], axis=1)
                                  .rename({'id': 'listener_id',
                                           'followers.total': 'num_followers'}, axis=1)
                     )
    listener_info['listener_image_url'] = profile_pic_url
    # remove commas
    listener_info['display_name'] = listener_info['display_name'].str.replace(
        ",", "")
    listener_info['username'] = listener_username
    return {"user_info": listener_info}


def clean_top_tracks_artist_info(new_user:SpotifyUser,
								 number_of_tracks:int=20,
								 time_range:str='short_term',
								 offset:int=0):
    """
    """
    top_tracks_json = new_user.get_top_tracks(number_of_tracks=number_of_tracks,
    										  time_range=time_range,
    										  offset=offset)['items']
    num_top_tracks = len(top_tracks_json)
    # all artists that correspond to top tracks
    top_track_created_by = []
    for i in range(num_top_tracks):
        track_id = json_normalize(top_tracks_json[i])['id'][0]
        artist = json_normalize(top_tracks_json[i]['artists'])
        artist['track_id'] = track_id
        top_track_created_by.append(artist)


    top_track_created_by = pd.concat(top_track_created_by, axis=0)
    # remove non unique rows 
    top_track_created_by= (top_track_created_by.drop_duplicates()
                                            .reset_index()
                                            .drop(['index', 'href', 'uri', 'external_urls.spotify', 'type'], axis=1)
                                            .rename({'id': 'artist_id',
                                                     'name': 'artist_name'}, 
                                                     axis=1)
    )

    # we must ensure that artists corresponding to top tracks are in the Artists table 
    top_track_artists_to_add = top_track_created_by[['artist_id', 'artist_name']].drop_duplicates()
    del top_track_created_by['artist_name']
    top_track_artists_to_add['artist_name'] = top_track_artists_to_add['artist_name'].str.replace(",", "")

    
    # TODO: GET THE REST OF ARTIST INFORMATION
    top_track_artists_to_add = json_normalize(new_user.sp.artists(top_track_artists_to_add['artist_id'])['artists'])     
    
    # get first image from the images url
    urls = top_track_artists_to_add.apply(lambda x: x['images'][0]['url'], axis=1)
    top_track_artists_to_add['artist_image_url'] = urls
    
    # rows already have unique id so no drop_duplicates() is necessary
    top_track_artists_to_add = (top_track_artists_to_add.reset_index()
                                            .drop(['index', 'href', 'uri', 'external_urls.spotify', 
                                                   'type', 'followers.href', 'type', 'images'], axis=1)
                                            .rename({'id': 'artist_id',
                                                     'name': 'artist_name',
                                                     'popularity': 'artist_pop',
                                                     'followers.total': 'num_followers'}, 
                                                     axis=1)
    )
    
    # add genre information when adding new artists
    top_track_artists_genres = top_track_artists_to_add.drop(['artist_name', 'artist_pop', 'num_followers', 'artist_image_url'], axis=1)
    genres_to_add = top_track_artists_genres.drop(['artist_id'], axis=1)

    # explode panda dataframes to eliminate lists in genres
    top_track_artists_genres = explode(top_track_artists_genres, lst_cols=['genres'])
    genres_to_add = explode(genres_to_add, lst_cols=['genres']).drop_duplicates()

    # remove genre information from artists, as genres are their own entity set
    top_track_artists_to_add = top_track_artists_to_add.drop(['genres'], axis=1)

    # reordering columns 
    top_track_created_by = top_track_created_by[["track_id", "artist_id"]]
    top_track_artists_to_add = top_track_artists_to_add[["artist_id", "artist_name", "artist_pop", "num_followers", "artist_image_url"]]
    top_track_artists_genres = top_track_artists_genres[["artist_id", "genres"]]

    # rename columns 
    top_track_artists_genres = top_track_artists_genres.rename({'genres':'genre_name'}, axis=1)
    genres_to_add = genres_to_add.rename({'genres':'genre_name'}, axis=1)

    #remove duplicate rows, fill empty strings
    top_track_artists_to_add.drop_duplicates(inplace=True)
    genres_to_add = genres_to_add.drop_duplicates().replace({"":"none"})
    top_track_artists_genres = top_track_artists_genres.replace({"":"none"})


    return {"top_track_created_by": top_track_created_by, 
            "top_track_artists_to_add": top_track_artists_to_add, 
            "top_track_genres_to_add": genres_to_add, 
            "top_track_artists_genres": top_track_artists_genres}


def clean_top_artists_info(new_user:SpotifyUser,
            						   number_of_artists:int=20,
            						   time_range:str='short_term', 
            						   offset:int=0):
    """
    """
    # generate artists to add table
    top_artists_to_add = json_normalize(new_user.get_top_artists(number_of_artists=number_of_artists,
    															 time_range=time_range,
    															 offset=offset)['items'])
    urls = top_artists_to_add.apply(lambda x: x['images'][0]['url'], axis=1)

    top_artists_to_add['artist_image_url'] = urls
    top_artists_to_add = (top_artists_to_add.drop(['href', 'type', 'uri', 'images',
                                                   'external_urls.spotify', 'followers.href'], axis=1)
                                            .rename({"followers.total": "num_followers",
                                                    "popularity": "artist_pop",
                                                    "id": "artist_id",
                                                    "name": 'artist_name'}, axis=1)
                  )
    # remove commas
    top_artists_to_add['artist_name'] = top_artists_to_add['artist_name'].str.replace(",", "")

    # generate top artists table 
    user_top_artists = top_artists_to_add[['artist_id']]

    # get listener id 
    listener_info = json_normalize(new_user.info())
    user_top_artists['listener_id'] = listener_info['id'][0]
    user_top_artists['time_span'] = time_range
    
    # all genres associated with artists
    genres_to_add = explode(top_artists_to_add[['genres']], lst_cols=['genres']).drop_duplicates()
    #     temp = pd.Series(genres_to_add)#set_index(['genres']).apply(pd.Series.explode).reset_index()
    #     genres_to_add = temp.explode()
    #     genres_to_add = genres_to_add.set_index('genres').apply(lambda x: x.apply(pd.Series).stack()).reset_index()

    # all artist, genre pairs for top artists
    top_artists_genres = explode(top_artists_to_add[['artist_id', 'genres']], lst_cols=['genres'])
    del top_artists_to_add['genres']

    # reorder columns 
    user_top_artists = user_top_artists[['listener_id', 'artist_id', 'time_span']]
    top_artists_to_add = top_artists_to_add[["artist_id", "artist_name", "artist_pop", "num_followers", "artist_image_url"]]
    top_artists_genres = top_artists_genres[['artist_id', 'genres']]

    # rename columns 
    top_artists_genres = top_artists_genres.rename({'genres':'genre_name'}, axis=1)
    genres_to_add = genres_to_add.rename({'genres':'genre_name'}, axis=1)

    # remove duplicate rows and clean nones
    top_artists_to_add.drop_duplicates(inplace=True)
    genres_to_add = genres_to_add.drop_duplicates().replace({"":"none"})
    top_artists_genres = top_artists_genres.replace({"":"none"})

    return {"user_top_artists": user_top_artists, 
            "top_artists_to_add": top_artists_to_add, 
            "top_artists_genres_to_add": genres_to_add, 
            "top_artists_genres": top_artists_genres}


def clean_top_tracks_album_info(new_user:SpotifyUser,
                								number_of_tracks:int=20,
                								time_range:str='short_term',
                								offset:int=0):
    '''
    '''
    # generic information about all top tracks 
    top_tracks_json = new_user.get_top_tracks(number_of_tracks=number_of_tracks,
    										  time_range=time_range,
    										  offset=offset)['items']

    top_tracks_df = json_normalize(top_tracks_json)
    user_top_tracks = (top_tracks_df.drop(['available_markets', 'disc_number', 'duration_ms',
                                       'explicit', 'href', 'is_local', 'type', 'uri', 'track_number',
                                       'album.album_type', 'album.artists', 'album.available_markets',
                                       'album.external_urls.spotify', 'album.href', 
                                      'album.images', 'album.name', 'album.release_date', 
                                      'album.release_date_precision', 'album.total_tracks', 
                                      'album.type', 'album.uri', 'external_ids.isrc',
                                      'external_urls.spotify', 'artists'], axis=1)
                                .rename({'id': 'track_id',
                                         'album.id': 'album_id', 
                                         'name': 'track_name',
                                         'popularity': 'track_pop'}, axis=1)
                 )
    # record the album that contains the track
    album_contains_track = user_top_tracks[['album_id', 'track_id']]
    del user_top_tracks['album_id']

    # we must ensure that top_tracks are put in the tracks table
    top_tracks_to_add = user_top_tracks

    # finalize top_tracks: add time range info, delete other extra attributes, add listener id
    user_top_tracks['time_span'] = time_range
    user_top_tracks = user_top_tracks.drop(['track_name',
    							  'track_pop', 
    							  'preview_url'], axis=1)
    
    listener_info = json_normalize(new_user.info())
    user_top_tracks['listener_id'] = listener_info['id'][0]



    # we must ensure that albums corresponding to top tracks are in the Albums table 
    urls = top_tracks_df.apply(lambda x: x['album.images'][0]['url'], axis=1)
    top_tracks_df['album_image_url'] = urls
    top_tracks_albums_to_add = (top_tracks_df
                                .drop(['available_markets', 'disc_number', 'duration_ms', 
                                       'explicit', 'href', 'is_local', 'type', 'uri', 'track_number',
                                       'album.available_markets',
                                       'album.external_urls.spotify', 'album.href', 
                                       'album.artists',
                                       'album.release_date_precision', 'album.total_tracks', 
                                       'album.type', 'album.uri', 'album.images',
                                       'id', 'name','popularity', 'preview_url',
                                       'external_ids.isrc',
                                       'external_urls.spotify', 'artists',
                                       ], axis=1)
                                .rename({'album.id': 'album_id',
                                          'album.album_type': 'album_type',
                                          'album.name': 'album_name', 
                                          'album.total_tracks': 'total_tracks',
                                          'album.type': 'album_type',
                                          'album.release_date': 'album_release_date'
                                          }, axis=1)
                               )
    # remove commas
    top_tracks_to_add['track_name'] = top_tracks_to_add['track_name'].str.replace(",", "")
    top_tracks_albums_to_add['album_name'] = top_tracks_albums_to_add['album_name'].str.replace(",", "")

    # delete time span for tracks to be added into Tracks entity set
    del top_tracks_to_add['time_span']

    # get track audio features
    top_track_ids = top_tracks_to_add[['track_id']]['track_id'].values.tolist()

    top_track_audio_features = json_normalize(new_user.get_track_audio_features(top_track_ids))
    top_track_audio_features = top_track_audio_features.drop(['analysis_url', 'key', 'duration_ms', 'type', 'uri', 'track_href'], axis=1).rename({'id':'track_id'}, axis=1)

    top_tracks_to_add = pd.merge(top_tracks_to_add, top_track_audio_features, on=['track_id'])

    top_track_album_ids = top_tracks_albums_to_add[['album_id']]['album_id'].values.tolist()

    top_track_album_info = json_normalize(new_user.get_album_info(top_track_album_ids))
    top_track_album_info = pd.DataFrame(top_track_album_info['albums'][0])

    top_tracks_album_genres = top_track_album_info.drop(['album_type', 'artists', 'available_markets', 'copyrights', 'external_urls', 'href', 'external_ids', 'name', 'label', 'popularity', 'release_date_precision', 'release_date', 'total_tracks', 'tracks', 'images', 'type', 'uri'], axis=1).rename({'id':'album_id'}, axis=1)
    top_tracks_album_genres = explode(top_tracks_album_genres, lst_cols=['genres'])

    genres_to_add = top_tracks_album_genres[['genres']]
    genres_to_add = explode(genres_to_add, lst_cols=['genres'])

    # reorder columns 
    user_top_tracks = user_top_tracks[['listener_id', 'track_id', 'time_span']]
    top_tracks_to_add = top_tracks_to_add[['track_id', 'track_name', 'track_pop', 
                                           'preview_url', 'acousticness', 'danceability', 
                                           'energy', 'valence', 'loudness', 'tempo', 
                                           'instrumentalness', 'speechiness', 'mode',
                                           'time_signature', 'liveness'
                                         ]]
    album_contains_track = album_contains_track[['album_id', 'track_id']]
    top_tracks_albums_to_add = top_tracks_albums_to_add[['album_id', 'album_type', 'album_name', 'album_release_date', 'album_image_url']]
    top_tracks_album_genres = top_tracks_album_genres[['album_id', 'genres']]

    # rename columns 
    top_tracks_album_genres = top_tracks_album_genres.rename({'genres':'genre_name'}, axis=1)
    genres_to_add = genres_to_add.rename({'genres':'genre_name'}, axis=1)

    # remove duplicate rows for tables with primary key constraint
    top_tracks_to_add.drop_duplicates(inplace=True)
    top_tracks_albums_to_add.drop_duplicates(inplace=True)
    genres_to_add = genres_to_add.drop_duplicates().replace({"":"none"})
    top_tracks_album_genres = top_tracks_album_genres.replace({"":"none"})


    return {"user_top_tracks": user_top_tracks, 
            "top_tracks_to_add": top_tracks_to_add, 
            "album_contains_track": album_contains_track, 
            "top_tracks_albums_to_add": top_tracks_albums_to_add, 
            "top_tracks_album_genres_to_add": genres_to_add, 
            "top_tracks_album_genres": top_tracks_album_genres}


def clean_all_data(new_user:SpotifyUser,
                   user_token_data:list):
    """
    Runs all the data cleaning functions, as though for a new user
    """
    user_info = clean_listener_info(new_user)
  
    user_info["user_info"]['access_token'] = user_token_data[0]
    user_info["user_info"]['scope'] = user_token_data[2]
    user_info["user_info"]['expires_in'] = user_token_data[3]
    user_info["user_info"]['refresh_token'] = user_token_data[-1]
    user_info["user_info"] = user_info["user_info"][["listener_id", 
                                                     "display_name",
                                                     "username",
                                                     "access_token",
                                                     "expires_in",
                                                     "refresh_token",
                                                     "scope", 
                                                     "num_followers",
                                                     "listener_image_url"]]

    top_tracks_artist_info = clean_top_tracks_artist_info(new_user) 
    top_tracks_album_info = clean_top_tracks_album_info(new_user)
    top_artists_info = clean_top_artists_info(new_user)

    data = {**user_info, 
            **top_tracks_artist_info, 
            **top_tracks_album_info, 
            **top_artists_info}

    return data