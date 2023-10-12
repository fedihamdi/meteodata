import xarray as xr
import pandas as pd
import numpy as np
import os
from src.era5_data_retriever import ERA5DataRetriever
from src.cams_data_retrieval import CAMSDataRetriever
from datetime import datetime

class DataProcessingJob:
    def __init__(self, start_date, end_date, path_to_data):
        self.start_date = start_date
        self.end_date = end_date
        self.path_to_data = path_to_data

    def normalize_coords(self, df, column):
        df[column] = df[column].apply(lambda x: ((x + 180) % 360) - 180)
        return df[column]

    def load_data(self):
        data_aq = xr.open_dataset(f"{self.path_to_data}/download.nc")
        data_th = xr.open_dataset(f"{self.path_to_data}/random_data.nc")
        data_precip = xr.open_dataset(f"{self.path_to_data}/random_data2.nc")
        data_pollen = xr.open_dataset(f"{self.path_to_data}/download_pollen_forcasts.nc")

        df_air_quality = data_aq.to_dataframe().reset_index()
        df_temp_humid = data_th.to_dataframe().reset_index()
        df_precip = data_precip.to_dataframe().reset_index()
        df_pollen = data_pollen.to_dataframe().reset_index()

        df_air_quality["time"] = pd.Timestamp(self.start_date).normalize() + df_air_quality["time"]
        df_temp_humid["time"] = pd.Timestamp(self.start_date).normalize() + df_temp_humid["time"]
        df_precip["time"] = pd.Timestamp(self.start_date).normalize() + df_precip["time"]
        df_pollen["time"] = pd.Timestamp(self.start_date).normalize() + df_pollen["time"]

        df_temp_humid["longitude"] = self.normalize_coords(df_temp_humid, "longitude")
        df_temp_humid["latitude"] = self.normalize_coords(df_temp_humid, "latitude")
        df_precip["longitude"] = self.normalize_coords(df_precip, "longitude")
        df_precip["latitude"] = self.normalize_coords(df_precip, "latitude")
        df_air_quality["longitude"] = self.normalize_coords(df_air_quality, "longitude")
        df_air_quality["latitude"] = self.normalize_coords(df_air_quality, "latitude")

        return df_air_quality, df_temp_humid, df_precip, df_pollen

    def merge_data(self, df1, df2):
        merged_df = ERA5DataRetriever().merge_dataframes_geometry(df1=df1, df2=df2, op="nearest")
        cols = ["time_left", "t_left", "r_left", "longitude", "latitude"]
        merged_df = merged_df[cols]
        column_mapping = {
            'time_left': 'time',
            't_left': 'temperature',
            'r_left': 'relative_humidity',
            'longitude': 'longitude',
            'latitude': 'latitude'
        }
        merged_df = merged_df.rename(columns=column_mapping)
        return merged_df

    def run(self):
        df_air_quality, df_temp_humid, df_precip, df_pollen = self.load_data()

        df_meteo = self.merge_data(df_temp_humid, df_precip)

        cols = ["time_left", "t_left", "r_left", "longitude", "latitude"]
        df_meteo = df_meteo[cols]
        column_mapping = {
            'time_left': 'time',
            't_left': 'temperature',
            'r_left': 'relative_humidity',
            'longitude': 'longitude',
            'latitude': 'latitude'
        }
        df_meteo = df_meteo.rename(columns=column_mapping)

        df_all = ERA5DataRetriever().merge_dataframes_geometry(df1=df_meteo, df2=df_air_quality, op="nearest")
        cols = ['time_left', 'temperature', 'relative_humidity', 'chocho_conc', 'co_conc', 'dust', 'ecres_conc',
                'ectot_conc', 'hcho_conc', 'nh3_conc', 'nmvoc_conc', 'no2_conc', 'no_conc', 'o3_conc', 'pans_conc',
                'pm10_conc', 'pm2p5_conc', 'pmwf_conc', 'sia_conc', 'so2_conc', 'longitude', 'latitude']
        df_all = df_all[cols]
        df_all = df_all.rename(columns={'time_left': 'time'})

        df_all.longitude = df_all.longitude.apply(lambda x: ((x + 180) % 360) - 180)
        df_all.latitude = df_all.latitude.apply(lambda x: ((x + 180) % 360) - 180)

        df_all_pol = ERA5DataRetriever().merge_dataframes_geometry(df1=df_all, df2=df_pollen, op="nearest")
        cols = ['time_left', 'temperature', 'relative_humidity', 'chocho_conc', 'co_conc', 'dust', 'ecres_conc',
                'ectot_conc', 'hcho_conc', 'nh3_conc', 'nmvoc_conc', 'no2_conc', 'no_conc', 'o3_conc', 'pans_conc',
                'pm10_conc', 'pm2p5_conc', 'pmwf_conc', 'sia_conc', 'so2_conc',
                'average_pollen_concentration', 'average_pollen_c_', 'average_pollen_c_1', 'longitude', 'latitude']
        df_all_pol = df_all_pol[cols]
        df_all_pol = df_all_pol.rename(columns={'time_left': 'time'})

        df_all_pol.to_csv(f"data_file_{self.start_date[:10]}.csv", index=False)

if __name__ == "__main__":
    start_date = '2022-07-10 00:00:00'
    end_date = '2022-07-11 00:00:00'
    path_to_data = os.getcwd()

    job = DataProcessingJob(start_date, end_date, path_to_data)
    job.run()