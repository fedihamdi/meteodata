import logging

import folium
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as opy
from django.shortcuts import render
from django_user_agents.utils import get_user_agent
from folium.plugins import HeatMap

from .filter_data import filter_data_user_position

logger_me = logging.getLogger(__name__)
logger_me.setLevel(logging.DEBUG)
token = "pk.eyJ1IjoiZmVkaWhhbWRpIiwiYSI6ImNrOGx2MzIxcTBhdWUzZm9raGdudzF1a2QifQ.E_Ho9zB0bqNqxApIB5n_QQ"


# def filter_data_user_position(only_data=False):
#     if not cache.get("my_data_key"):
#         path = os.path.join(
#             os.path.abspath(os.path.join(os.getcwd(), os.pardir)),
#             "data_nc",
#             "data_file_20231116.parquet",
#         )
#         df = pd.read_parquet(path, engine="pyarrow")  # pd.read_csv(path)#
#         geocoder.ip("me")
#         # if g.latlng is None :
#         user_latitude, user_longitude = [48.8534, 2.4488]
#         # else :
#         # user_latitude, user_longitude = g.latlng
#         filtered_df = df[
#             (round(df["latitude"]) == round(user_latitude))
#             & (round(df["longitude"]) == round(user_longitude))
#         ]
#         pollen_estimated = round(filtered_df["average_pollen_concentration"].mean(), 2)
#         if pd.isna(pollen_estimated):
#             pollen_estimated = 0
#             filtered_df["average_pollen_concentration"].fillna(0, inplace=True)
#         else:
#             logger_me.info(
#                 f"estimated pollen concentration is available {pollen_estimated}"
#             )
#         cache.set("my_data_key", df, 3600)
#         cache.set("my_data_key", filtered_df, 3600)
#     else:
#         df = cache.get("my_data_key")
#         filtered_df = df
#
#     if only_data:
#         return [filtered_df, user_latitude, user_longitude, pollen_estimated]
#     else:
#         return filtered_df


def estimation_data_view():
    data = filter_data_user_position(only_data=False)
    estimation_view = round(data.average_pollen_concentration.mean(), 2)
    co_view = round(data.co_conc.mean(), 2)
    o3_view = round(data.o3_conc.mean(), 2)
    pm10_view = round(data.pm10_conc.mean(), 2)
    context1 = {
        "estimation_view": estimation_view,
        "carbon_monoxide": co_view,
        "ozone_view": o3_view,
        "pm10_view": pm10_view,
    }
    return context1  # render(request, 'pages/index.html', context1)


def pollen_data_view(request):
    (
        filtered_df,
        user_latitude,
        user_longitude,
        pollen_estimated,
    ) = filter_data_user_position(only_data=True)

    user_agent = get_user_agent(request)
    is_mobile = user_agent.is_mobile
    if not is_mobile:
        fig = px.density_mapbox(
            filtered_df,
            lat="latitude",
            lon="longitude",
            z="average_pollen_concentration",
            hover_name="average_pollen_concentration",
            center=dict(lat=user_latitude, lon=user_longitude),
            zoom=10,
            radius=100,
            opacity=0.7,
            mapbox_style="dark",
            # animation_frame="time",
            # color_continuous_scale="Bluered",
            # animation_group="average_pollen_concentration",
        )
        fig.update_layout(legend_title="Pollen C° and position")
        fig.add_trace(
            go.Scattermapbox(
                lat=[user_latitude],
                lon=[user_longitude],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=14,
                    color="blue",
                ),
                name="User Location",
                customdata=[pollen_estimated],
            )
        )
        fig.add_trace(
            go.Scattermapbox(
                lat=[user_latitude],
                lon=[user_longitude],
                mode="markers",
                marker=go.scattermapbox.Marker(size=pollen_estimated * 10, opacity=0.2),
                name=f"Estimation {round(pollen_estimated,2)}",
                hoverinfo="text",
                text=[f"Estimation: {round(pollen_estimated, 2)}"],
            )
        )

        fig.update_layout(
            mapbox=dict(center=dict(lat=user_latitude, lon=user_longitude), zoom=9.5)
        )
        fig.update_layout(
            coloraxis_colorbar=dict(  # yanchor="top", xanchor="left",y=1, x=0.5, ticks="outside",
                title="Pollen C°"
            )
        )
        # fig.update_coloraxes(colorbar_orientation='h')
        # fig.update_traces(coloraxis_colorbar=dict(orientation='h', yanchor='bottom', y=1.02), colorscale='Viridis')

        fig.update_layout(mapbox=dict(style="satellite-streets", accesstoken=token))
        context2 = {
            "pollen_fig": fig.to_json(engine="json"),
            "pollen_map": opy.plot(
                fig, auto_open=True, output_type="div"
            ),  # fig.to_html(),
            "data_snap": data_snapshot(filtered_df, "average_pollen_concentration"),
            "data_snap_nitro": data_snapshot(filtered_df, "no2_conc"),
        }
    else:
        pollen_map = folium.Map(location=[user_latitude, user_longitude], zoom_start=10)

        # Ajoutez une couche de densité avec les données de concentration de pollen
        heat_data = [
            [row["latitude"], row["longitude"], row["average_pollen_concentration"]]
            for index, row in filtered_df.iterrows()
        ]
        heat_data.append([user_latitude, user_longitude, pollen_estimated])
        HeatMap(
            heat_data,
            radius_fixed=True,
            radius=100,
            opacity=0.5,
        ).add_to(pollen_map)

        # Ajoutez un marqueur pour la position de l'utilisateur
        folium.Marker(
            location=[user_latitude, user_longitude],
            popup=f"User Location\nPollen Estimation: {round(pollen_estimated, 2)}",
            icon=folium.Icon(color="blue"),
        ).add_to(pollen_map)

        # Convertissez la carte en HTML
        map_html = pollen_map._repr_html_()
        context2 = {
            # "pollen_fig": fig.to_json(engine="json"),
            "pollen_map": map_html,
            "data_snap": data_snapshot(filtered_df, "average_pollen_concentration"),
            "data_snap_nitro": data_snapshot(filtered_df, "no2_conc"),
        }

    context2.update(estimation_data_view())
    return render(request, "pages/index.html", context2)


def data_snapshot(dataframe, column):
    return dataframe[column].values.tolist()[:7]


def index(request):
    # page from the them
    return render(request, "pages/index.html")
