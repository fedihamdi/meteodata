import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px

st.set_page_config(
    page_title="POC pollen ",
    page_icon="photo.jpg",
    initial_sidebar_state="expanded",
)

st.sidebar.title("POC Breatheeasy")


@st.cache_data
def load_data(path=os.getcwd()[:-8] + "\\data_file_2022-07-10.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


df_ = load_data()

# show data

st.write(df_.head(10))
st.write(os.getcwd())

fig = px.density_mapbox(
    df_,
    lat="latitude",
    lon="longitude",
    z="average_pollen_c_",
    hover_name="average_pollen_c_",
    center=dict(lat=0, lon=180),
    zoom=0,
    radius=10,
    opacity=0.7,
    mapbox_style="dark",
    # animation_frame='time',
)

# Customize the layout (e.g., title)
fig.update_layout(
    title="Pollen breach worldwide",
    mapbox=dict(
        center=dict(
            lat=20, lon=70
        ),  # Set the initial center and zoom level for the mapbox
        zoom=1.5,
    ),
)

fig.update_layout(mapbox_style="open-street-map")
st.plotly_chart(fig)
