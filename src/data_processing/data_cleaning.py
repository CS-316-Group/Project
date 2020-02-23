import pandas as pd
import numpy as np
from pandas.io.json import json_normalize

from data_processing.spotify_user import SpotifyUser


def clean_listener_info(new_user:SpotifyUser):
    """
    """
    listener_info = json_normalize(new_user.info())

    profile_pic_url = listener_info['images'][0][0]['url']

    user_type = listener_info['type'][0]
    assert user_type == 'user', f'Individual type must be user, instead is {user_type}'
    listener_info = (listener_info.drop(['href', 'images', 'uri', 'external_urls.spotify', 'type', 'followers.href'], axis=1)
                                  .rename({'id': 'listener_id',
                                           'followers.total': 'num_followers'}, axis=1)
                     )
    listener_info['listener_image_url'] = profile_pic_url
    # remove commas
    listener_info['display_name'] = listener_info['display_name'].str.replace(
        ",", "")
    return listener_info


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
    top_track_artists_to_add_json = new_user.artists(top_track_artists_to_add['artist_id'])
    print(top_track_artists_to_add_json)
    return top_track_created_by, top_track_artists_to_add


def clean_top_artists_info(new_user:SpotifyUser,
						   number_of_tracks:int=20, 
						   time_range:str='short_term', 
						   offset:int=0):
    """
    """
    # generate artists to add table
    top_artists_to_add = json_normalize(new_user.get_top_artists(number_of_tracks=number_of_tracks,
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
    top_artists = top_artists_to_add[["artist_id"]]

    # get listener id 
    listener_info = json_normalize(new_user.info())
    top_artists['listener_id'] = listener_info['id'][0]
    top_artists['time_span'] = time_range
    
    # TODO: CREATE A GENRES ENTITY 
    del top_artists_to_add['genres']

    return top_artists, top_artists_to_add


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
    top_tracks = (top_tracks_df.drop(['available_markets', 'disc_number', 'duration_ms', 
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

    album_contains_track = top_tracks[['album_id', 'track_id']]
    del top_tracks['album_id']
    # add time range info 
    top_tracks['time_span'] = time_range

    # we must ensure that albums corresponding to top tracks are in the Albums table 
    urls = top_tracks_df.apply(lambda x: x['album.images'][0]['url'], axis=1)
    top_tracks_df['album_image_url'] = urls
    top_tracks_albums_to_add = (top_tracks_df
                                .drop(['available_markets', 'disc_number', 'duration_ms', 
                                       'explicit', 'href', 'is_local', 'type', 'uri', 'track_number',
                                       'album.available_markets',
                                       'album.external_urls.spotify', 'album.href', 
                                       'album.release_date', 'album.artists',
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
                                          'album.type': 'album_type'
                                          }, axis=1)
                               )
    # remove commas
    top_tracks['track_name'] = top_tracks['track_name'].str.replace(",", "")
    top_tracks_albums_to_add['album_name'] = top_tracks_albums_to_add['album_name'].str.replace(",", "")

    return top_tracks, album_contains_track, top_tracks_albums_to_add
