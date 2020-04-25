import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import datetime 

from d00_utils.explode import explode
from d01_data_processing.spotify_user import SpotifyUser

NULL_KEYWORD = 'NULL'


def clean_listener_info(new_user:SpotifyUser, new_password:str):
    """
    """
    listener_username = new_user.username
    listener_info = json_normalize(new_user.info())

    if (len(listener_info['images'][0]) > 0):
        profile_pic_url = listener_info['images'][0][0]['url']
    else:
        profile_pic_url = NULL_KEYWORD

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
    listener_info['display_name'] = listener_info['display_name'].str.replace(",", "")
    listener_info['username'] = listener_username
    listener_info['password'] = new_password

    return {"user_info": listener_info}


def clean_top_tracks_artist_info(new_user:SpotifyUser,
                                 number_of_tracks:int=20,
                                 offset:int=0):
    """
    """
    top_track_created_by = []
    for time_range in ['short_term', 'medium_term', 'long_term']:

        top_tracks_json = new_user.get_top_tracks(number_of_tracks=number_of_tracks,
                                                  time_range=time_range,
                                                  offset=offset)['items']
        num_top_tracks = len(top_tracks_json)
        # all artists that correspond to top tracks
        for i in range(num_top_tracks):
            track_id = json_normalize(top_tracks_json[i])['id'][0]
            artist = json_normalize(top_tracks_json[i]['artists'])
            artist['track_id'] = track_id
            top_track_created_by.append(artist)
            
    # check if no top tracks exist for any time ranges 
    if top_track_created_by == []: 
        return {"top_track_created_by": pd.DataFrame({}), 
                "top_track_artists_to_add": pd.DataFrame({}), 
                "top_track_genres_to_add": pd.DataFrame({}), 
                "top_track_artists_genres": pd.DataFrame({})}

    top_track_created_by = pd.concat(top_track_created_by, axis=0)

    # remove non unique rows 
    top_track_created_by= (top_track_created_by.reset_index()
                                               .drop(['index', 'href', 'uri', 'external_urls.spotify', 
                                                      'type', 'name'], axis=1)
                                               .rename({'id': 'artist_id'}, 
                                                        axis=1)
    )

    # we must ensure that artists corresponding to top tracks are in the Artists table 
    top_track_artists_to_add = chunk_api_requests(ids=top_track_created_by['artist_id'],
                                                  sp_user_class_method=new_user.sp.artists,
                                                  selection_attr='artists')

    top_track_artists_to_add['name'] = top_track_artists_to_add['name'].str.replace(",", "")
    
    # get first image from the images url
    urls=[]
    for row in top_track_artists_to_add.iterrows():
        try: 
            urls.append(row[1]['images'][0]['url'])
        except Exception as e: 
            urls.append(NULL_KEYWORD)
    top_track_artists_to_add['artist_image_url'] = urls
    
    # rows already have unique id so no drop_duplicates() is necessary
    top_track_artists_to_add = (top_track_artists_to_add.reset_index()
                                                        .drop(['index', 'href', 'uri', 'external_urls.spotify', 
                                                               'type', 'followers.href', 'type', 'images'], axis=1)
                                                        .rename({'id': 'artist_id',
                                                                 'name': 'artist_name',
                                                                 'popularity': 'artist_pop',
                                                                 'followers.total': 'num_followers',
                                                                 'genres': 'genre_name'}, 
                                                                axis=1)
                                                        .astype({'artist_pop': 'int32'})
    )
    
    # add genre information when adding new artists
    top_track_artists_genres = top_track_artists_to_add.drop(['artist_name', 'artist_pop', 
                                                              'num_followers', 'artist_image_url'], 
                                                              axis=1)
    genres_to_add = top_track_artists_genres.drop(['artist_id'], axis=1)

    # explode panda dataframes to eliminate lists in genres
    top_track_artists_genres = explode(top_track_artists_genres, lst_cols=['genre_name'])
    genres_to_add = explode(genres_to_add, lst_cols=['genre_name'])

    # remove genre information from artists, as genres are their own entity set
    top_track_artists_to_add = top_track_artists_to_add.drop(['genre_name'], axis=1)

    # reordering columns 
    top_track_created_by = top_track_created_by[["track_id", "artist_id"]]
    top_track_artists_to_add = top_track_artists_to_add[["artist_id", "artist_name", 
                                                        "artist_pop", "num_followers", 
                                                        "artist_image_url"]]
    top_track_artists_genres = top_track_artists_genres[["artist_id", "genre_name"]]

    # cleanup
    results = {"top_track_created_by": top_track_created_by, 
               "top_track_artists_to_add": top_track_artists_to_add, 
               "top_track_genres_to_add": genres_to_add, 
               "top_track_artists_genres": top_track_artists_genres}

    results = remove_nulls_drop_dups(results)
    return results


def clean_top_artists_info(new_user:SpotifyUser,
                           number_of_artists:int=20,
                           offset:int=0):
    """
    """
    # generate artists to add table
    top_artists_to_add = []
    for time_range in ['short_term', 'medium_term', 'long_term']:
        artists_df = json_normalize(new_user.get_top_artists(number_of_artists=number_of_artists,
                                                                          time_range=time_range,
                                                                          offset=offset)['items'])
        artists_df['time_span'] = time_range
        top_artists_to_add.append(artists_df)

    top_artists_to_add = pd.concat(top_artists_to_add, axis=0)

    # check if no top artists 
    if len(top_artists_to_add) == 0:
        return {"user_top_artists": pd.DataFrame({}), 
                "top_artists_to_add": pd.DataFrame({}), 
                "top_artists_genres_to_add": pd.DataFrame({}), 
                "top_artists_genres": pd.DataFrame({})}

    # get first image from the images url
    urls=[]
    for row in top_artists_to_add.iterrows():
        try: 
            urls.append(row[1]['images'][0]['url'])
        except Exception as e: 
            urls.append(NULL_KEYWORD)

    top_artists_to_add['artist_image_url'] = urls
    top_artists_to_add = (top_artists_to_add.drop(['href', 'type', 'uri', 'images',
                                                   'external_urls.spotify', 'followers.href'], axis=1)
                                            .rename({"followers.total": "num_followers",
                                                    "popularity": "artist_pop",
                                                    "id": "artist_id",
                                                    "name": 'artist_name',
                                                    "genres": "genre_name"}, axis=1)
                                            .astype({'artist_pop':'int32'})
                  )
    # remove commas
    top_artists_to_add['artist_name'] = top_artists_to_add['artist_name'].str.replace(",", "")

    # generate top artists table 
    user_top_artists = top_artists_to_add[['artist_id', 'time_span']]

    # get listener id 
    listener_info = json_normalize(new_user.info())
    user_top_artists['listener_id'] = listener_info['id'][0]
    
    # all genres associated with artists
    genres_to_add = explode(top_artists_to_add[['genre_name']], lst_cols=['genre_name'])

    # all artist, genre pairs for top artists
    top_artists_genres = explode(top_artists_to_add[['artist_id', 'genre_name']], 
                                 lst_cols=['genre_name'])
    del top_artists_to_add['genre_name']

    # reorder columns 
    user_top_artists = user_top_artists[['listener_id', 'artist_id', 'time_span']]
    top_artists_to_add = top_artists_to_add[["artist_id", "artist_name", 
                                             "artist_pop", "num_followers", 
                                             "artist_image_url"]]
    top_artists_genres = top_artists_genres[['artist_id', 'genre_name']]

    # cleanup
    results = {"user_top_artists": user_top_artists, 
               "top_artists_to_add": top_artists_to_add, 
               "top_artists_genres_to_add": genres_to_add, 
               "top_artists_genres": top_artists_genres}

    results = remove_nulls_drop_dups(results)


    return results


def clean_top_tracks_album_info(new_user:SpotifyUser,
                                number_of_tracks:int=20,
                                offset:int=0):
    '''
    '''
    # generic information about all top tracks 
    top_tracks_df = []
    for time_range in ['short_term', 'medium_term', 'long_term']:
        top_tracks = json_normalize(new_user.get_top_tracks(number_of_tracks=number_of_tracks,
                                                  time_range=time_range,
                                                  offset=offset)['items'])
        top_tracks['time_span'] = time_range
        top_tracks_df.append(top_tracks)
    top_tracks_df = pd.concat(top_tracks_df, axis=0)
    
    # check if there are any top tracks
    if len(top_tracks_df) == 0: 
        return {"user_top_tracks": pd.DataFrame({}), 
                "top_tracks_to_add": pd.DataFrame({}), 
                "album_contains_track": pd.DataFrame({}), 
                "top_tracks_albums_to_add": pd.DataFrame({}), 
                "top_tracks_album_genres_to_add": pd.DataFrame({}), 
                "top_tracks_album_genres": pd.DataFrame({})}

    user_top_tracks = (top_tracks_df[['id', 'album.id', 'name', 'popularity', 'preview_url', 'time_span']]
                                .rename({'id': 'track_id',
                                         'album.id': 'album_id', 
                                         'name': 'track_name',
                                         'popularity': 'track_pop'}, axis=1)
                                .astype({'track_pop': 'int32'})
                      )
    # record the album that contains the track
    album_contains_track = user_top_tracks[['album_id', 'track_id']]
    del user_top_tracks['album_id']

    # we must ensure that top_tracks are put in the tracks table
    top_tracks_to_add = user_top_tracks.copy()
    del top_tracks_to_add['time_span']
    top_tracks_to_add['track_name'] = top_tracks_to_add['track_name'].str.replace(",", "")
    
    # del extra attr from user_top_tracks, add listener id, add audio features 
    user_top_tracks = user_top_tracks.drop(['track_name', 'track_pop', 'preview_url'], 
                                           axis=1)
    listener_info = json_normalize(new_user.info())
    user_top_tracks['listener_id'] = listener_info['id'][0]
    
    # get top_tracks audio features
    top_track_audio_features = chunk_api_requests(ids=top_tracks_to_add['track_id'], 
                                                  sp_user_class_method=new_user.get_track_audio_features, 
                                                  )

    top_track_audio_features = (top_track_audio_features.drop(['analysis_url', 'key', 'duration_ms', 
                                                              'type', 'uri', 'track_href'], 
                                                              axis=1)
                                                       .rename({'id':'track_id'}, 
                                                               axis=1))

    top_tracks_to_add = pd.merge(top_tracks_to_add, top_track_audio_features, on=['track_id'])

    # we must ensure that albums corresponding to top tracks are in the Albums table 
    urls=[]
    for row in top_tracks_df.iterrows():
        try: 
            urls.append(row[1]['album.images'][0]['url'])
        except Exception as e: 
            urls.append(NULL_KEYWORD)

    top_tracks_df['album_image_url'] = urls
    top_tracks_albums_to_add = (top_tracks_df[['album.id', 'album.album_type', 'album.name', 
                                               # 'album.type', 
                                               'album.release_date', 'album_image_url']]
                                .rename({'album.id': 'album_id',
                                          'album.album_type': 'album_type',
                                          'album.name': 'album_name', 
                                          # 'album.type': 'album_type',
                                          'album.release_date': 'album_release_date'
                                          }, axis=1)
                               )
    
    top_tracks_albums_to_add['album_name'] = top_tracks_albums_to_add['album_name'].str.replace(",", "")
    top_tracks_albums_to_add['album_release_date'] = pd.to_datetime(top_tracks_albums_to_add['album_release_date'])

    # get genre info for albums
    top_track_album_info = chunk_api_requests(ids=top_tracks_albums_to_add['album_id'], 
                                              sp_user_class_method=new_user.get_album_info, 
                                              selection_attr='albums'
                                              )
    
    top_tracks_album_genres = (top_track_album_info[['id', 'genres']]
                                                  .rename({'id':'album_id',
                                                           'genres': 'genre_name'}, 
                                                          axis=1))
    top_tracks_album_genres = explode(top_tracks_album_genres, lst_cols=['genre_name'])
    genres_to_add = explode(top_tracks_album_genres[['genre_name']], lst_cols=['genre_name'])

    # reorder columns 
    user_top_tracks = user_top_tracks[['listener_id', 'track_id', 'time_span']]
    top_tracks_to_add = top_tracks_to_add[['track_id', 'track_name', 'track_pop', 
                                           'preview_url', 'acousticness', 'danceability', 
                                           'energy', 'valence', 'loudness', 'tempo', 
                                           'instrumentalness', 'speechiness', 'mode',
                                           'time_signature', 'liveness'
                                         ]]

    album_contains_track = album_contains_track[['album_id', 'track_id']]
    top_tracks_albums_to_add = top_tracks_albums_to_add[['album_id', 'album_type', 'album_name', 
                                                         'album_release_date', 'album_image_url']]
    top_tracks_album_genres = top_tracks_album_genres[['album_id', 'genre_name']]

    results = {"user_top_tracks": user_top_tracks, 
               "top_tracks_to_add": top_tracks_to_add, 
               "album_contains_track": album_contains_track, 
               "top_tracks_albums_to_add": top_tracks_albums_to_add, 
               "top_tracks_album_genres_to_add": genres_to_add, 
               "top_tracks_album_genres": top_tracks_album_genres}
    results = remove_nulls_drop_dups(results)

    return results 


def remove_nulls_drop_dups(df_dict):
    for df_name in df_dict.keys(): 
        df_dict[df_name] = df_dict[df_name].replace({"":NULL_KEYWORD,
                                                     None:NULL_KEYWORD})
        df_dict[df_name] = df_dict[df_name].drop_duplicates()

    return df_dict 


def chunk_api_requests(ids, sp_user_class_method, 
                       api_n_limit=20, 
                       selection_attr=None):
    res_df = []
    num_chunks = np.ceil(len(ids)/api_n_limit)
    for id_chunk in np.array_split(ids, num_chunks):
        json = sp_user_class_method(id_chunk)
        if selection_attr is not None: 
            json = json[selection_attr]
        res_df.append(json_normalize(json))
    return pd.concat(res_df, axis=0) 


def clean_all_data(new_user:SpotifyUser,
                   new_password:str,
                   user_token_data:list, 
                   number_of_tracks:int=20,
                   number_of_artists:int=20,
                   time_range:str='long_term',
                   offset:int=0):
    """
    Runs all the data cleaning functions, as though for a new user
    """
    user_info = clean_listener_info(new_user, new_password)
  
    user_info["user_info"]['access_token'] = user_token_data[0]
    user_info["user_info"]['scope'] = user_token_data[2]
    user_info["user_info"]['expires_in'] = user_token_data[3]
    user_info["user_info"]['refresh_token'] = user_token_data[-1]
    user_info["user_info"]['creation_datetime'] = datetime.datetime.utcnow()
    user_info["user_info"] = user_info["user_info"][["listener_id", 
                                                     "display_name",
                                                     "username",
                                                     "password",
                                                     "access_token",
                                                     "expires_in",
                                                     "refresh_token",
                                                     "scope", 
                                                     "creation_datetime", 
                                                     "num_followers",
                                                     "listener_image_url"]]

    top_tracks_artist_info = clean_top_tracks_artist_info(new_user=new_user,
                                                          number_of_tracks=number_of_tracks,
                                                          offset=offset) 
    top_tracks_album_info = clean_top_tracks_album_info(new_user=new_user,
                                                        number_of_tracks=number_of_tracks,
                                                        offset=offset)
    top_artists_info = clean_top_artists_info(new_user=new_user,
                                              number_of_artists=number_of_artists,
                                              offset=offset)

    data = {**user_info, 
            **top_tracks_artist_info, 
            **top_tracks_album_info, 
            **top_artists_info}

    return data
