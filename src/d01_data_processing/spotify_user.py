import spotipy
import sys
import spotipy.util as util


class SpotifyUser:
    """
    This class defines a Spotify user. A user is identified
    by their username and will need to give authorization under
    certain scopes for the other methods to be called. Once 
    authorization is given, multiple methods will obtain user 
    related information from Spotify.
    """
    def __init__(self, username, from_scratch,
                 spotipy_client_id=None, 
                 spotipy_client_secret=None, 
                 spotipy_redirect_uri=None, 
                 # OR
                 token=None):
        """
        Two methods to initialize a SpotifyUser: either by directly passing in access token, 
        or initializing a SpotifyUser "from scratch" by passing in developer creds. 
        """
        self.username = username


        if from_scratch: 
            scope = 'user-library-read user-follow-read user-top-read user-read-recently-played'
            self.token = util.prompt_for_user_token(username, 
                                                    scope, 
                                                    spotipy_client_id, 
                                                    spotipy_client_secret, 
                                                    spotipy_redirect_uri)
        
        else: 
            assert token is not None, "Must pass in token."
            self.token=token

        #verify that user authorization was successful
        try: 
            self.sp = spotipy.Spotify(auth=self.token)
        except Exception as e:
            print("ERROR: User authorization unsuccessful.")



    def info(self):
        if self.token:
            return self.sp.me()
        else:
            raise Exception("ERROR: Cannot get user info when user", self.username, "has not given authorization.")
            
    def get_most_recent_tracks(self, number_of_tracks=20):
        '''
        Returns some of the most recently played tracks.
        number_of_tracks controls how many tracks are returned.
        DOES NOT CURRENTLY WORK - I am not sure why
        '''
        if self.token:
            return self.sp.current_user_recently_played(number_of_tracks)
        else:
            raise Exception("ERROR: Cannot get most recent tracks when user", self.username, "has not given authorization.")

    def get_saved_tracks(self, number_of_tracks=20, offset=0):
        '''
        Returns a limited number of the user's saved tracks.
        number_of_tracks controls how many tracks are returned at a time.
        You can use the offset parameter to get songs starting after a certain song number.
        This allows us to retrieve all songs by querying for a limited number of tracks at a
        time and looping.
        ''' 
        if self.token:
            return self.sp.current_user_saved_tracks(number_of_tracks, offset)
        else:
            raise Exception("ERROR: Cannot get saved tracks when user", self.username, "has not given authorization.")
            
    def get_saved_albums(self, number_of_albums=20, offset=0):
        '''
        Returns a limited number of the user's saved albums.
        number_of_albums controls how many albums are returned at a time.
        You can use the offset parameter to get albums starting after a certain song number.
        This allows us to retrieve all albums by querying for a limited number of tracks at a
        time and looping.
        '''
    
        if self.token:
            return self.sp.current_user_saved_albums(number_of_albums, offset)
        else:
            raise Exception("ERROR: Cannot get saved albums when user", self.username, "has not given authorization.")
    
    def get_followed_artists(self, number_of_artists=20, after=None):
        '''
        Returns a limited number of the artists followed by the current user.
        number_of_artists controls how many artists are retrieved at a time.
        You can use the after parameter to get artists starting after a certain artists id
        To get all followed artists, you need to get x artists at a time, then get the next
        x artists starting after the last artist in the previous query.
        '''
        if self.token:
            return self.sp.current_user_followed_artists(number_of_artists, after)
        else:
            raise Exception("ERROR: Cannot get followed artists when user", self.username, "has not given authorization.")
    
    def get_top_tracks(self, number_of_tracks=20, time_range='short_term', offset=0):
        '''
        Returns the most popular tracks for the current user.
        number_of_tracks controls how many tracks are returned.
        time_range = {'short_term', 'medium_term', 'long_term'} controls whether we get the most 
         recent popular songs, somewhat recent popular songs, or long-term popular songs.
        offset controls the starting point, allowing us to say get the 20-40 most popular tracks.
         I assume we will not need to use offset for our purposes so I set the default value to 0.
        '''
        if self.token:
            return self.sp.current_user_top_tracks(number_of_tracks, offset, time_range)
        else:
            raise Exception("ERROR: Cannot get top tracks when user", self.username, "has not given authorization.")        
    
    def get_top_artists(self, number_of_artists=20, time_range='short_term', offset=0):
        '''
        Returns the most popular artists for the current user.
        number_of_artists controls how many tracks are returned.
        time_range = {'short_term', 'medium_term', 'long_term'} controls whether we get the most 
         recent popular artists, somewhat recent popular artists, or long-term popular artists.
        offset controls the starting point, allowing us to say get the 20-40 most popular tracks.
         I assume we will not need to use offset for our purposes so I set the default value to 0.    
        '''
        if self.token:
            return self.sp.current_user_top_artists(number_of_artists, offset, time_range)
        else:
            raise Exception("ERROR: Cannot get top artists when user", self.username, "has not given authorization.")  

    def get_track_audio_features(self, track_ids):
        '''
        Given a list of track ids, returns an set of audio features for each track,
        such as energy, liveliness, speechiness, tempo, etc.
        '''
        if self.token:
            return self.sp.audio_features(track_ids)
        else:
            raise Exception("ERROR: Cannot get audio features for tracks when user", self.username, "has not given authorization.")  

    def get_album_info(self, album_ids):
        '''
        Given a list of album ids, returns album info for each album.
        '''
        if self.token:
            return self.sp.albums(album_ids)
        else:
            raise Exception("ERROR: Cannot get info for albums when user", self.username, "has not given authorization.")  