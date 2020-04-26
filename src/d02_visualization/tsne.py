import pandas as pd
import numpy as np
from sklearn.manifold import TSNE as TSNE
import matplotlib.pyplot as plt
import json
import plotly
import plotly.graph_objs as go


def makeComparisonGraph(af):
    af_numeric = af.copy
    del af_numeric['listener_id']

    af_numeric_embedded = TSNE(n_components=2).fit_transform(af_numeric)
    tsne_x = np.zeros(len(af_numeric.index))
    tsne_y = np.zeros(len(af_numeric.index))

    for i in range(len(af_numeric_embedded)):
        tsne_x[i] = af_numeric_embedded[i][0]
        tsne_y[i] = af_numeric_embedded[i][1]

    af_numeric['tsne_x'] = tsne_x
    af_numeric['tsne_y'] = tsne_y
    names = af['listener_id']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tsne_x,
        y=tsne_y,
        mode="markers",
        hovertext=names
    ))

    fig.update_layout(title_text="Spotify Share Music Taste Universe")
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    data3 = [fig]
    graphJSON3 = json.dumps(data3, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON3
