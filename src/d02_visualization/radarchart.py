import pandas as pd
import plotly.express as px
import numpy as np
import json
import plotly
import matplotlib.pyplot as plt
from plotly import tools
import plotly.graph_objs as go

def makeRadarChart(af,listenerID):
    afListener = af[af['listener_id'] == listenerID]

    genre_categories_1 = ['is_pop', 'is_hip_hop', 'is_rock', 'is_classical', 'is_country', 'is_christian', 'is_edm','is_r&b_soul','is_alternative']
    song_quality_categories = ['avg_acousticness','avg_danceability','avg_energy','avg_instrumentalness', 'avg_speechiness','avg_artist_pop','%_major']

    genre_values_1 = afListener[genre_categories_1].values[0]
    song_quality_values = afListener[song_quality_categories].values[0]

    #Rename categories
    genre_categories_1 = ['Pop', 'Hip Hop', 'Rock', 'Classical', 'Country', 'Christian', 'EDM','R&B Soul','Alternative']
    song_quality_categories = ['Avg. Acousticness','Avg. Danceability','Energy','Instrumentalness', 'Speechiness','Artist Popularity','Percent Major Modality']
 
    data1 = [go.Scatterpolar(r=genre_values_1, theta=genre_categories_1, 
                fill = 'toself',
                line =  dict(color = 'orange'),  
                showlegend = False)]

    graphJSON1 = json.dumps(data1, cls=plotly.utils.PlotlyJSONEncoder)

    data2 = [go.Scatterpolar(r=song_quality_values, theta=song_quality_categories, 
                fill = 'toself',
                line =  dict(color = 'red'),  
                showlegend = False)]

    graphJSON2 = json.dumps(data2, cls=plotly.utils.PlotlyJSONEncoder)

    # fig1 = px.line_polar(r=genre_values_1, theta=genre_categories_1, line_close=True, range_r=[0, 1], title='Genres')
    # fig1.update_traces(fill='toself')
    # fig2 = px.line_polar(r=song_quality_values, theta=song_quality_categories, line_close=True, range_r=[0, 1], title='Music Attributes')
    # fig2.update_traces(fill='toself')

    return (graphJSON1,graphJSON2)