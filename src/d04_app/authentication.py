import os
os.chdir('../src/')
print("Current working directory is now: ", os.getcwd())

import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
from IPython.display import display

from d01_data_processing.data_cleaning import *
from d01_data_processing.spotify_user import SpotifyUser
from utils.load_confs import load_credentials


def authenticate():
    spotify_creds = load_credentials()['spotify_dev_creds']

    # spotify = spotipy.Spotify()
    new_username = 'selen'
    new_user = SpotifyUser(spotify_creds['spotify_client_id'],
                           spotify_creds['spotify_client_secret'],
                           'http://localhost:8889',
                           new_username)

    top_track_created_by, top_track_artists_to_add = clean_top_tracks_artist_info(new_user)

    display(top_track_artists_to_add.head())
    display(top_track_created_by.head())
