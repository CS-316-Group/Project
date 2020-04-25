import pandas as pd
import plotly.express as px

def makeRadarChart(af,listenerID):
    afListener = af[af['listener_id'] == listenerID]

    genre_categories_1 = ['is_pop', 'is_hip_hop', 'is_rock', 'is_classical', 'is_country', 'is_christian', 'is_edm','is_r&b_soul','is_alternative']
    song_quality_categories = ['avg_acousticness','avg_danceability','avg_energy','avg_instrumentalness', 'avg_speechiness','avg_artist_pop','%_major']

    genre_values_1 = afListener[genre_categories_1].values[0]
    song_quality_values = afListener[song_quality_categories].values[0]

    fig1 = px.line_polar(r=genre_values_1, theta=genre_categories_1, line_close=True, range_r=[0, 1], title='Genres')
    fig1.update_traces(fill='toself')
    fig2 = px.line_polar(r=song_quality_values, theta=song_quality_categories, line_close=True, range_r=[0, 1], title='Music Attributes')
    fig2.update_traces(fill='toself')

    return (fig1,fig2)