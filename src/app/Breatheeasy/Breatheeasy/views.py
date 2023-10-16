from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import geocoder
import csv

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

    # Create the density map
    traces = []

    # Iterate over the columns of the filtered DataFrame
    for column in filtered_df.columns:
        # Create a scatter plot trace for the current column
        trace = go.Scattermapbox(
            lat=filtered_df['latitude'],
            lon=filtered_df['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14,  # You can adjust the size as needed
                opacity=0.7,  # You can adjust the opacity as needed
            ),
            name=column,  # Set the trace name to the column name
            text=filtered_df[column].astype(str),  # Display the column's data as text on hover
        )

        traces.append(trace)

    # Update map layout
    user_latitude, user_longitude = g.latlng
    layout = go.Layout(
        mapbox=dict(
            center=dict(lat=user_latitude, lon=user_longitude),
            zoom=10.5,

        ),
        mapbox_style="open-street-map",
    )

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