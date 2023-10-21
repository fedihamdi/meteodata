from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.core.cache import cache
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import geocoder
import logging
from .forms import PollenUserLog

logger_me = logging.getLogger(__name__)
logger_me.setLevel(logging.DEBUG)


def filter_data_user_position(only_data=False):
    df = None
    filtered_df = None
    if not cache.get("my_data_key"):
        path = os.path.join(os.getcwd()[:-20], "data_file_2022-07-10.csv")
        df = pd.read_csv(path)
        g = geocoder.ip("me")
        user_latitude, user_longitude = g.latlng
        filtered_df = df[
            (round(df["latitude"]) == round(user_latitude))
            & (round(df["longitude"]) == round(user_longitude))
        ]
        pollen_estimated = filtered_df.average_pollen_concentration.mean()
        cache.set("my_data_key", df, 3600)
        cache.set("my_data_key", filtered_df, 3600)
    if df is None or filtered_df is None:
        df = cache.get("my_data_key")
    if only_data:

        try:
            return [filtered_df, user_latitude, user_longitude, pollen_estimated]
        except:
            logger_me.info(
                [filtered_df, user_latitude, user_longitude, pollen_estimated]
            )
            logger_me.warning("This is failing 1")
    else:
        logger_me.info("This is failing 2")
        return filtered_df


def columns_data_view():

    data = filter_data_user_position(only_data=False).head(3)

    try:
        columns_view = data.columns.to_list()
        context = {
            "options": columns_view,
        }
        return columns_view  # render(request, 'pollen_page.html', context)
    except:
        logger_me.warning("This is failing 3")


def pollen_data_view(request):

    try:
        filtered_df = pd.DataFrame()
        (
            filtered_df,
            user_latitude,
            user_longitude,
            pollen_estimated,
        ) = filter_data_user_position(only_data=True)
    except Exception as e:
        logger_me.warning(f"This is failing 4" f"{e}")
    fig = px.density_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        z="average_pollen_c_",
        hover_name="average_pollen_c_",
        center=dict(lat=user_latitude, lon=user_longitude),
        zoom=10,
        radius=100,
        opacity=0.7,
        mapbox_style="dark",
        title="Pollen breach worldwide",
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=[user_latitude],
            lon=[user_longitude],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=14,
                color="blue",
            ),
            name=f"User Location",
            customdata=[pollen_estimated],
        )
    )
    fig.add_trace(
        go.Scattermapbox(
            lat=[user_latitude],
            lon=[user_longitude],
            mode="markers",
            marker=go.scattermapbox.Marker(size=pollen_estimated * 10, opacity=0.2),
            name=f"Estimation {pollen_estimated}",
        )
    )

    fig.update_layout(
        mapbox=dict(center=dict(lat=user_latitude, lon=user_longitude), zoom=9.5)
    )

    fig.update_layout(mapbox_style="open-street-map")

    context = {"pollen_fig": fig.to_html(), "options": columns_data_view()}

    return render(request, "pollen_page.html", context)


def user_signup(request):
    form = PollenUserLog()
    context = {"first_form": form}
    return render(request, "signup_page.html", context)
