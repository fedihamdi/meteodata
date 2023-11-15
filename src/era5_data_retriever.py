import logging
import os
from datetime import datetime, timedelta

import cdsapi
import geopandas as gpd
import pandas as pd
import xarray as xr
from dotenv import load_dotenv
from shapely.geometry import Point

load_dotenv()
logger = logging.getLogger(__name__)


def extract_date_components(start_date, end_date):
    # TODO: use the is_valid_date_format pour la prochaine iteration/opti du code
    # TODO: il faut trouver une solution pour ne pas charecher des dates qui non pas de sens
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")

    years = []
    months = []
    days = []

    current_date = start_date_obj
    while current_date <= end_date_obj:
        year_str = str(current_date.year)
        month_str = str(current_date.month).zfill(2)
        day_str = str(current_date.day).zfill(2)

        if year_str not in years:
            years.append(year_str)
        if month_str not in months:
            months.append(month_str)
        if day_str not in days:
            days.append(day_str)

        current_date += timedelta(days=1)

    return years, months, days


class ERA5DataRetriever:
    def __init__(
        self,
        variables=["temperature", "total_precipitation", "relative_humidity"],
        year=None,
        month=None,
        day=None,
        time="12:00",
        start_date=None,
        end_date=None,
    ):
        ERA5_URL = os.environ.get("CDSAPI_URL_ERA5")  # env vars pour la cnx API CAMS
        ERA5_KEY = os.environ.get("CDSAPI_KEY_ERA5")
        if year is None or month is None or day is None:
            if start_date is not None and end_date is not None:
                year, month, day = extract_date_components(start_date, end_date)
            else:
                # peut etre mettre des loggers au cas ou ca tourne mal
                raise ValueError(
                    "Either provide 'year', 'month', and 'day', or 'start_date' and 'end_date'"
                )
        logger.warning(f"You are now looking for data {year} {month} {day}")

        self.c = cdsapi.Client(url=ERA5_URL, key=ERA5_KEY)
        self.variables = variables
        self.pressure_level = "1000"
        self.product_type = "reanalysis"
        self.year = year
        self.month = month
        self.day = day
        self.time = time
        self.format = "netcdf"

    def retrieve_data(
        self,
        variable_list=None,
        output_filename="file_.nc",
        database="reanalysis-era5-pressure-levels",
    ):
        if variable_list is None:
            variable_list = self.variables
        lis = ["reanalysis-era5-pressure-levels", "reanalysis-era5-single-levels"]
        if database not in lis:
            raise ValueError(f"Type must be {lis}")

        request_params = {
            "variable": variable_list,
            "pressure_level": self.pressure_level,
            "product_type": self.product_type,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "time": self.time,
            "format": self.format,
            "area": [51.99, -8.45, 41.57, 13.86],
        }
        self.c.retrieve(database, request_params, output_filename)

    def open_dataset(self, filename):
        return xr.open_dataset(filename)

    def merge_dataframes(self, df1, df2, on=["longitude", "latitude", "time"]):
        return pd.merge(df1, df2, on=["longitude", "latitude", "time"], how="inner")

    def merge_dataframes_geometry(self, df1, df2, op="nearest"):
        df1["geometry"] = df1.apply(
            lambda row: Point(row["longitude"], row["latitude"]), axis=1
        )
        df2["geometry"] = df2.apply(
            lambda row: Point(row["longitude"], row["latitude"]), axis=1
        )

        df1 = gpd.GeoDataFrame(df1, geometry="geometry")
        df2 = gpd.GeoDataFrame(df2, geometry="geometry")
        joined_gdf = gpd.sjoin_nearest(df1, df2)
        joined_gdf = joined_gdf.drop(columns=["geometry"])
        joined_gdf["longitude"] = joined_gdf.apply(
            lambda x: (x["longitude_left"] + x["longitude_right"]) / 2, axis=1
        )
        joined_gdf["latitude"] = joined_gdf.apply(
            lambda x: (x["latitude_left"] + x["latitude_right"]) / 2, axis=1
        )
        joined_gdf = joined_gdf.drop(
            columns=[
                "latitude_left",
                "latitude_right",
                "longitude_right",
                "longitude_left",
            ]
        )
        return joined_gdf
