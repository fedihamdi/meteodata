import cdsapi
import xarray as xr
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

class ERA5DataRetriever:
    def __init__(self, variables=['temperature', 'total_precipitation', 'relative_humidity'],
                 year=2008, month="01", day="01",time="12:00"):
        self.c = cdsapi.Client()
        self.variables = variables
        self.pressure_level = "1000"
        self.product_type = "reanalysis"
        self.year = year
        self.month = month
        self.day = day
        self.time = time
        self.format = "netcdf"

    def retrieve_data(self, variable_list, output_filename):
        request_params = {
            "variable": variable_list,
            "pressure_level": self.pressure_level,
            "product_type": self.product_type,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "time": self.time,
            "format": self.format,
        }
        self.c.retrieve("reanalysis-era5-pressure-levels", request_params, output_filename)

    def open_dataset(self, filename):
        return xr.open_dataset(filename)

    def merge_dataframes(self, df1, df2, on=['longitude', 'latitude', 'time']):
        return pd.merge(df1, df2, on=['longitude', 'latitude', 'time'], how="inner")

    def merge_dataframes_geometry(self, df1, df2, op='nearest'):
        df1['geometry'] = df1.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
        df2['geometry'] = df2.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)

        df1 = gpd.GeoDataFrame(df1, geometry='geometry')
        df2 = gpd.GeoDataFrame(df2, geometry='geometry')
        joined_gdf = gpd.sjoin_nearest(df1, df2)
        joined_gdf = joined_gdf.drop(columns=['geometry'])
        joined_gdf["longitude"] = joined_gdf.apply(lambda x: (x["longitude_left"] + x["longitude_right"]) / 2, axis=1)
        joined_gdf["latitude"] = joined_gdf.apply(lambda x: (x["latitude_left"] + x["latitude_right"]) / 2, axis=1)
        joined_gdf = joined_gdf.drop(columns=['latitude_left', 'latitude_right', 'longitude_right', 'longitude_left'])
        return joined_gdf
