from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import geocoder

def pollen_data_view(request):
    df = None
    filtered_df = None
    if not cache.get('my_data_key'):
        path = os.path.join(os.getcwd()[:-20], 'data_file_2022-07-10.csv')
        df = pd.read_csv(path)
        g = geocoder.ip('me')
        user_latitude, user_longitude = g.latlng
        filtered_df = df[(round(df['latitude']) == round(user_latitude)) & (round(df['longitude']) == round(user_longitude))]
        pollen_estimated = filtered_df.average_pollen_concentration.mean()
        cache.set('my_data_key', df, 3600)
        cache.set('my_data_key', filtered_df, 3600)
    if df is None or filtered_df is None:
        df = cache.get('my_data_key')

    fig = px.density_mapbox(
        filtered_df,
        lat='latitude',
        lon='longitude',
        z="average_pollen_c_",
        hover_name='average_pollen_c_',
        center=dict(lat=user_latitude, lon=user_longitude),
        zoom=10,
        radius=100,
        opacity=0.7,
        mapbox_style="dark", title='Pollen breach worldwide',
    )

    fig.add_trace(go.Scattermapbox(
        lat=[user_latitude],
        lon=[user_longitude],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14,
            color='blue',
        ),
        name=f'User Location',
        customdata=[pollen_estimated]
    ))
    fig.add_trace(go.Scattermapbox(
        lat=[user_latitude],
        lon=[user_longitude],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=pollen_estimated * 10,
            opacity=0.2
        ),
        name=f'Estimation {pollen_estimated}'
    ))

    fig.update_layout(

        mapbox=dict(
            center=dict(lat=user_latitude, lon=user_longitude),
            zoom=10.5
        )
    )

    fig.update_layout(mapbox_style="open-street-map")

    context = {
        'pollen_fig': fig.to_html(),
    }

    return render(request, 'pollen_page.html', context)