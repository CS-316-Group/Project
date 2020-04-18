import pandas as pd 
import numpy as np 

from d03_database_interaction.db_operations import select_from_table


# TODO: put these parameters in the parameters.yml
num_tracks = 20
time_frame = 'long_term'


####### COMPUTE TOP TRACKS FEATURES FOR INDIVIDUAL 
def compute_inv_pop(series):
    '''compute average weighted by the idf of track_pop
    vec is a pd series of integers from 0 to 100'''
    return np.log(100/series).replace({np.inf: 5.7})
        

def compute_track_features(track_info:pd.DataFrame,
                           num_tracks=num_tracks):
    """
    computes the features for an individual 
    """
    # top tracks track features 
    # avg weighted by the track inverse popularity 
    col_list= ['acousticness', 'danceability', 'energy', 
                'valence', 'loudness', 'tempo', 'instrumentalness',
                'speechiness', 'time_signature', 'liveness'] 
    track_info['inv_pop'] = compute_inv_pop(track_info['track_pop'])
    features_tracks_dict = {f"avg_{col}": np.average(track_info[col],
                                                     weights=track_info['inv_pop']) 
                            for col in col_list}
    # features_dict
    features_tracks_dict["%_major"] = np.sum(track_info['mode'])/num_tracks
    return features_tracks_dict

######### COMPUTE TOP ARTIST FEATURES FOR INDIVIDUAL 
genre_map = {
                # new
                'alternative': 'alternative', 
                'indie': 'alternative', 
                'experimental': 'experimental', 
                'avant': 'experimental', 
                
                # typical gentres 
                'country': 'country', 
                'folk': 'country', 
                'rock': 'rock', 
                'punk': 'rock', 
                'metal': 'metal',
                'rap': 'hip_hop', 
                'hip': 'hip_hop', 
                'hop': 'hip_hop',
                'trap': 'hip_hop', 
                'pop': 'pop', 
                
                # r&b, african-american insp. 
                'r&b': 'r&b_soul', 
                'soul': 'r&b_soul', 
                'funk': 'r&b_soul',
                'afro': 'jazz', 
                'jazz': 'jazz',
                
                # religious 
                'gospel': 'christian', 
                'christian': 'christian', 

                # ethnic
                'reggae': 'latin', 
                'latin': 'latin', 
                 
                # soundtrack 
                'soundtrack': 'soundtrack',
                'video': 'soundtrack', 
                'score': 'soundtrack',
                'tunes': 'soundtrack', 
                'cartoon': 'soundtrack', 
                'anime': 'soundtrack', 
                'otacore': 'soundtrack',
                
                # classical type / vocal
                'classical': 'classical', 
                'orchestra': 'classical',                
                'chamber': 'classical', 
                'contemporary': 'contemporary', 
                # vocal
                'capella': 'vocal',
                'choir': 'vocal',
                'alto': 'vocal',
                'soprano': 'vocal', 
                'vocal': 'vocal',
                
                # electronic 
                'edm': 'edm', 
                'rave': 'edm', 
                'house': 'edm', 
                'tech': 'edm',
                'room': 'edm',
                'step': 'edm', 
                'dance': 'edm', 
                'electronic': 'edm',
                'trance': 'edm',
                
                # misc chill : 
                'lo-fi': 'chill',
                'meditation': 'chill', 
                'drone': 'chill', 
                'focus': 'chill', 
                'zen': 'chill'
               }

def invert_dictionary(adict:dict):
    '''keys->values, values->keys'''
    inv_map = {}
    for k, v in adict.items():
        inv_map[v] = inv_map.get(v, [])
        inv_map[v].append(k)
    return inv_map


def compute_artists_features(artist_info:pd.DataFrame, 
                             genre_map:dict, 
                             num_tracks=num_tracks):
    '''compute the top artists features for an individual'''

    genre_str_arr = np.array(artist_info['genre_name'], dtype=str)
    inv_genre_map = invert_dictionary(genre_map)
    
    for genre, subgenres in inv_genre_map.items(): 
        # test for subgenre in each entry of genre_str_arr
        subgenre_bool_filters = []
        for subgen in subgenres: 
            subgenre_bool_filters.append((np.core.defchararray.find(genre_str_arr, 
                                                                    subgen) != -1))
        # elementwise logical or on all subgenre boolean arrays 
        logical_or_bool = np.logical_or.reduce(subgenre_bool_filters)
        artist_info[f"is_{genre}"] = logical_or_bool

    artist_genres = artist_info.copy()
    del artist_genres['genre_name']
    artist_genres = artist_genres.groupby(['artist_id', 'artist_pop', 'num_followers']).any()

    features_artists_dict = (artist_genres.reset_index().drop(['artist_id', 'artist_pop', 'num_followers'], axis=1).sum()/num_tracks).to_dict()
    # compute avg artist popularity and rescale
    features_artists_dict['avg_artist_pop'] = np.mean(artist_info['artist_pop'])/100

    return features_artists_dict


######### COMPUTE ALL FEATURES FOR ALL INDIVIDUALS 
def retrieve_feature_data_all(db_engine,
                              time_frame=time_frame):
    """Runs SQL commands to retrieve the 
    data for computing features from the database 
    """
    track_cmd = f"""
              select toptrack_info.listener_id, 
                   track_pop, acousticness, 
                   danceability, energy, valence, 
                   loudness, tempo, 
                   instrumentalness, speechiness, 
                   mode, time_signature, liveness
              from tracks as t1
              natural join 
                (select t2.track_id, t2.listener_id
                 from toptracks as t2
                 where time_span='{time_frame}'
                )
              as toptrack_info
             """

    top_track_info = select_from_table(sql=track_cmd,
                                       db_engine=db_engine)

    artist_cmd = f"""
               select * 
               from artisthasgenre 
               natural join 
                  (select topartist_info.listener_id, a1.artist_id, a1.artist_pop, a1.num_followers 
                   from artists as a1
                   natural join 
                      (select topart.listener_id, topart.artist_id
                       from topartists as topart 
                       where time_span='{time_frame}')
                   as topartist_info) 
               as artist_info
               """

    top_artist_info = dl.select_from_table(sql=artist_cmd,
                                           db_engine=db_engine)

    return top_track_info, top_artist_info


def compute_features_all(top_track_info:pd.DataFrame, 
                         top_artist_info:pd.DataFrame,
                         genre_map=genre_map,
                         num_tracks=num_tracks):
    '''Computes the features for all individuals in database 
    top_track_info 
    Returns pandas dataframe 
    '''
    # typecast columns to numeric 
    cols = list(top_track_info.columns)
    cols.remove('listener_id')
    top_track_info[cols] = top_track_info[cols].apply(pd.to_numeric, errors='coerce')

    # get listener ids
    a = set(top_track_info['listener_id'])
    b = set(top_artist_info['listener_id'])
    listener_ids = a|b 

    features_df = []
    for listener_id in listener_ids:
        track_listener_info = top_track_info[top_track_info["listener_id"] == listener_id]
        artist_listener_info = top_artist_info[top_artist_info["listener_id"] == listener_id]
        
        track_feat = compute_track_features(track_listener_info,
                                            num_tracks=num_tracks)
        artist_feat = compute_artists_features(artist_listener_info, 
                                               genre_map=genre_map,
                                               num_tracks=num_tracks)

        features = {**track_feat, 
                    **artist_feat} 
        features['listener_id'] =  listener_id
                    
        
        features_df.append(features)

    features_df = pd.DataFrame(features_df)
    return features_df