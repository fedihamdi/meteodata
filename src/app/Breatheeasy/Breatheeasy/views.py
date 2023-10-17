from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import geocoder
import csv


# Define a mapping of column names to display names
column_mapping = {
    'time': 'Temps',
    'temperature': 'Température',
    'relative_humidity': 'Humidité relative',
    'chocho_conc': 'Éthanedial',
    'dust': 'Poussières',
    'ecres_conc': 'Suie / carbone élémentaire',
    'hcho_conc': 'formaldéhyde',
    'no2_conc': 'Dioxyde d\'azote',
    'nh3_conc': 'Ammoniac',
    'no_conc': 'monoxyde d\'azote',
    'nmvoc_conc': 'Composés organiques volatils non méthaniques',
    'o3_conc': 'Ozone',
    'co_conc': 'Monoxyde de carbone',
    'ectot_conc': 'Total de carbon élementaire',
    'pans_conc': 'Nitrate de peroxyacétyle',
    'pm10_conc': 'Micro particules < 10 µm',
    'pm2p5_conc': 'Micro particules < 2.5 µm',
    'pmwf_conc': 'Display Name 2',
    'sia_conc': 'Display Name 2',
    'so2_conc': 'Dioxyde de soufre',
    'average_pollen_concentration': 'Concentration moyenne pollens',
    'longitude': 'Longitude',
    'latitude': 'Latitude',
}

exclude_columns = ["longitude", "latitude", "time", "average_pollen_c_", "average_pollen_c_1"]


def pollen_data_view(request):
    df = None
    filtered_df = None

    if not cache.get('my_data_key'):
        path = os.path.join(os.getcwd()[:-20], 'data_file_2022-07-10.csv')
        df = pd.read_csv(path)
        df['temperature'] = round(df['temperature'] - 273.15, 1)
        g = geocoder.ip('me')
        user_latitude, user_longitude = g.latlng
        filtered_df = df[(round(df['latitude']) == round(user_latitude)) & (round(df['longitude']) == round(user_longitude))]
        pollen_estimated = filtered_df.average_pollen_concentration.mean()
        cache.set('my_data_key', df, 3600)
        cache.set('my_data_key', filtered_df, 3600)

    if df is None or filtered_df is None:
        df = cache.get('my_data_key')

        # Add the map subplot (in the middle)
        fig.add_trace(px.density_mapbox(
            filtered_df,
            lat='latitude',
            lon='longitude',
            z="average_pollen_c_",
            hover_name='average_pollen_c_',
            center=dict(lat=user_latitude, lon=user_longitude),
            zoom=10,
            radius=100,
            opacity=0.7,
            mapbox_style="dark",
            title='Pollen breach worldwide',
        ).data[0], row=1, col=2)


        # Update the layout to make it look nice
        fig.update_layout(
            showlegend=False,
            height=500,  # Set the height of the plot as needed
        )


    traces = []

    # Iterate over the columns of the filtered DataFrame
    for column in filtered_df.columns:
        if column in exclude_columns:
            continue

        if column in column_mapping:
            display_name = column_mapping[column]
        else:
            display_name = column  # Use the original column name if not mapped

        # Create a scatter plot trace for the current column
        trace = go.Scattermapbox(
            lat=filtered_df['latitude'],
            lon=filtered_df['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14,
                opacity=0.7,
            ),
            name=display_name,
            text=filtered_df[column].astype(str),
            hoverinfo='text'
        )

        custom_color_scale = ['#FF0000', '#FF3300', '#FF6600', '#FF9900', '#FFCC00', '#FFCC33', '#FFCC66', '#FFCC99',
                              '#FFCCBB', '#99CC00', '#66CC00', '#33CC00']

        trace_min_value = filtered_df[column].min()
        trace_max_value = filtered_df[column].max()
        normalized_values = (filtered_df[column] - trace_min_value) / (trace_max_value - trace_min_value)
        color_indices = [int(val * (len(custom_color_scale) - 1)) for val in normalized_values]
        marker_colors = [custom_color_scale[idx] for idx in color_indices]

        # Create a scatter plot trace with marker colors
        trace = go.Scattermapbox(
            lat=filtered_df['latitude'],
            lon=filtered_df['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14,
                opacity=0.7,
                color=marker_colors,  # Assign the marker colors here
                colorbar=dict(title=display_name),
            ),
            name=display_name,
            text=filtered_df[column].astype(str),
            hoverinfo='text'
        )

        traces.append(trace)

    # Update map layout with width and height
    layout = go.Layout(
        mapbox=dict(
            center=dict(lat=user_latitude, lon=user_longitude),
            zoom=10.5,
        ),
        mapbox_style="open-street-map",
        width= 1150,
        height= 880,
    )


    # Create the figure with all the traces
    fig = go.Figure(data=traces, layout=layout)
    fig.update_layout(coloraxis_colorbar=dict(yanchor="top", y=1, x=-1, ticks="outside"))

    context = {
        'pollen_fig': fig.to_html(),
    }

    return render(request, 'pollen_page.html', context)

# ======================================================================================================================

def generate_checkbox_html(csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        column_names = next(csv_reader)  # Read the header row

        checkbox_html = ""

        for column_name in column_names:
            checkbox_html += f'<label><input type="checkbox" name="{column_name}" value="{column_name}"> {column_name}</label><br>'

    return checkbox_html


def filters_form_view(request):

    csv_file_path = os.path.join(os.getcwd()[:-20], 'data_file_2022-07-10.csv')
    checkbox_html = generate_checkbox_html(csv_file_path)
    return render(request, 'checkbox_form.html', {'checkbox_html': checkbox_html})


def generate_plot(selected_columns):
    csv_path = os.path.join(os.getcwd()[:-20], 'data_file_2022-07-10.csv')
    data = pd.read_csv(csv_path)

    # Always include "longitude" and "latitude" in the selected columns
    selected_columns.extend(["longitude", "latitude"])

    # Create a subset of the data based on selected columns
    subset_data = data[selected_columns]

    # Create a Plotly plot using Plotly Express
    fig = px.scatter(subset_data, x='longitude', y='latitude')

    return fig.to_html(full_html=False)


def plotly_plot_view(request):
    selected_columns = request.GET.getlist('column_name') # Get selected checkboxes as a list
    plotly_plot_html = generate_plot(selected_columns)


    return render(request, 'plotly_plot.html', {'plotly_plot_html': plotly_plot_html})
