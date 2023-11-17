# dashapp.py
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from django_plotly_dash import DjangoDash

from .filter_data import filter_data_user_position

token = "pk.eyJ1IjoiZmVkaWhhbWRpIiwiYSI6ImNrOGx2MzIxcTBhdWUzZm9raGdudzF1a2QifQ.E_Ho9zB0bqNqxApIB5n_QQ"
(
    filtered_df,
    user_latitude,
    user_longitude,
    pollen_estimated,
) = filter_data_user_position(only_data=True)

app = DjangoDash("SimpleExample")

# Sample data
(
    filtered_df,
    user_latitude,
    user_longitude,
    pollen_estimated,
) = filter_data_user_position(only_data=True)
zoom = 10
fig = px.density_mapbox(
    filtered_df,
    lat="latitude",
    lon="longitude",
    z="average_pollen_concentration",
    hover_name="average_pollen_concentration",
    center=dict(lat=user_latitude, lon=user_longitude),
    zoom=zoom,
    radius=100 / (2 ** (10 - zoom)),
    opacity=0.7,
    mapbox_style="dark",
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
fig.update_layout(coloraxis_colorbar=dict(title="Pollen C°"))
fig.update_layout(mapbox=dict(style="satellite-streets"))

app.layout = html.Div(
    [
        dcc.Graph(id="pollen-map", figure=fig),
        html.Div(
            [
                dcc.Graph(id="other-graph"),  # Add other Dash components as needed
            ]
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
