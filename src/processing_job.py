import os
import xarray as xr
import pandas as pd
from era5_data_retriever import ERA5DataRetriever
from azure.storage.blob import BlobServiceClient, BlobClient
import time
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

connectionString = os.environ.get('BLOB_CONNECTION_STRING')
containerName = "output"
outputDirectory = "temp"  # Directory to store downloaded .nc files

class DataProcessingJob:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.client = ERA5DataRetriever(start_date=start_date, end_date=end_date)
        self.blob_service_client = BlobServiceClient.from_connection_string(connectionString)
        self.container_client = self.blob_service_client.get_container_client(containerName)
        self.output_directory = outputDirectory

    def normalize_coords(self, df, column):
        df[column] = ((df[column] + 180) % 360) - 180
        return df[column]

    def open_blob_as_dataset(self, blob_name):
        with BlobClient.from_connection_string(conn_str=connectionString, container_name=containerName,
                                               blob_name=blob_name) as blob_client:
            download_stream = blob_client.download_blob()
            content = download_stream.readall()

            if not os.path.exists(outputDirectory):
                os.makedirs(outputDirectory)

            blob_path = os.path.join(outputDirectory, blob_name)
            with open(blob_path, "wb") as file:
                file.write(content)

            dataset = None
            while dataset is None:
                try:
                    logger.warning("reading started")
                    dataset = xr.open_dataset(blob_path, engine='netcdf4')
                    logger.warning("reading completed")
                except PermissionError:
                    logger.warning("Failed loading the data due to size issue")
                    time.sleep(5)

            time.sleep(5)
            dataset.close()
            pandas_df = dataset.to_dataframe().reset_index()
            os.remove(blob_path)

        return pandas_df

    def load_data(self):
        df_air_quality = df_temp_humid = df_precip = df_pollen = None

        for blob in self.container_client.list_blobs():
            if "era5_data_temp_humidity_" in blob.name:
                df_temp_humid = self.open_blob_as_dataset(blob.name)
                logger.warning("Reading df_temp_humid is done")
            elif "era5_data_precip_" in blob.name:
                df_precip = self.open_blob_as_dataset(blob.name)
                logger.warning("Reading df_precip is done")
            elif "cams_data_air_quality_" in blob.name:
                df_air_quality = self.open_blob_as_dataset(blob.name)
                logger.warning("Reading df_air_quality is done")
            elif "cams_data_pollen_" in blob.name:
                df_pollen = self.open_blob_as_dataset(blob.name)
                logger.warning("Reading df_pollen is done")

        if df_air_quality is not None:
            df_air_quality["time"] = pd.Timestamp(self.start_date).normalize() + df_air_quality["time"]
            df_air_quality["longitude"] = self.normalize_coords(df_air_quality, "longitude")
            df_air_quality["latitude"] = self.normalize_coords(df_air_quality, "latitude")
            df_air_quality = df_air_quality.loc[df_air_quality.time.between(self.start_date, self.end_date), ]

        if df_temp_humid is not None:
            df_temp_humid["longitude"] = self.normalize_coords(df_temp_humid, "longitude")
            df_temp_humid["latitude"] = self.normalize_coords(df_temp_humid, "latitude")
            df_temp_humid = df_temp_humid.loc[df_temp_humid.time.between(self.start_date, self.end_date), ]

        if df_precip is not None:
            df_precip["longitude"] = self.normalize_coords(df_precip, "longitude")
            df_precip["latitude"] = self.normalize_coords(df_precip, "latitude")
            df_precip = df_precip.loc[df_precip.time.between(self.start_date, self.end_date), ]

        if df_pollen is not None:
            df_pollen["time"] = pd.Timestamp(self.start_date).normalize() + df_pollen["time"]
            df_pollen["longitude"] = self.normalize_coords(df_pollen, "longitude")
            df_pollen["latitude"] = self.normalize_coords(df_pollen, "latitude")
            df_pollen = df_pollen.loc[df_pollen.time.between(self.start_date, self.end_date), ]

        return df_air_quality, df_temp_humid, df_precip, df_pollen

    def merge_data(self, df1, df2):
        client = self.client
        merged_df = client.merge_dataframes_geometry(df1=df1, df2=df2, op="nearest")

        return merged_df

    def run(self):
        df_air_quality, df_temp_humid, df_precip, df_pollen = self.load_data()

        df_meteo = self.merge_data(df_precip, df_temp_humid)
        del df_temp_humid, df_precip

        cols = ["time_left", "t", "r", "tp", "longitude", "latitude"]
        df_meteo = df_meteo[cols]
        column_mapping = {
            'time_left': 'time',
            't': 'temperature',
            'r': 'relative_humidity',
            'tp': 'total_precipitations',
            'longitude': 'longitude',
            'latitude': 'latitude'
        }
        df_meteo = df_meteo.rename(columns=column_mapping)
        client = self.client

        df_all = client.merge_dataframes_geometry(df1=df_meteo, df2=df_air_quality, op="nearest")
        del df_meteo, df_air_quality
        cols = ['time_left', 'temperature', 'relative_humidity', 'total_precipitations', 'co_conc', 'dust',
                'ecres_conc',
                'ectot_conc', 'nh3_conc', 'nmvoc_conc', 'no2_conc', 'no_conc', 'o3_conc', 'pans_conc',
                'pm10_conc', 'pm2p5_conc', 'pmwf_conc', 'sia_conc', 'so2_conc', 'longitude', 'latitude']
        df_all = df_all[cols]
        df_all = df_all.rename(columns={'time_left': 'time'})

        df_all.longitude = self.normalize_coords(df_all, "longitude")
        df_all.latitude = self.normalize_coords(df_all, "latitude")

        exclude_columns = ['apg_conc', 'bpg_conc', 'gpg_conc', 'mpg_conc',
                           'opg_conc', 'rwpg_conc']
        df_pollen['average_pollen_concentration'] = df_pollen.loc[:, df_pollen.columns.isin(exclude_columns)].mean(
            axis=1)
        df_pollen["average_pollen_c_"] = df_pollen.average_pollen_concentration.apply(
            lambda x: float("{:.2e}".format(x)))

        df_all_pol = client.merge_dataframes_geometry(df1=df_all, df2=df_pollen, op="nearest")
        del df_all, df_pollen
        cols = ['time_left', 'temperature', 'relative_humidity', 'co_conc', 'dust', 'ecres_conc',
                'ectot_conc', 'nh3_conc', 'nmvoc_conc', 'no2_conc', 'no_conc', 'o3_conc', 'pans_conc',
                'pm10_conc', 'pm2p5_conc', 'pmwf_conc', 'sia_conc', 'so2_conc',
                'apg_conc', 'bpg_conc', 'gpg_conc', 'mpg_conc',
                'opg_conc', 'rwpg_conc',
                'average_pollen_concentration', 'average_pollen_c_', 'longitude', 'latitude']
        df_all_pol = df_all_pol[cols]
        df_all_pol = df_all_pol.rename(columns={'time_left': 'time'})

        # Save the processed data to Parquet
        output_filename = f"data_file_{self.start_date[:10]}.parquet"
        output_path = os.path.join(self.output_directory, output_filename)
        df_all_pol.to_parquet(output_path, index=False)

        # Upload the processed data to Azure Blob Storage
        output_blob_name = f"data/{output_filename}"
        blob = BlobClient.from_connection_string(conn_str=connectionString, container_name=containerName, blob_name=output_blob_name)
        with open(output_path, "rb") as data:
            blob.upload_blob(data, overwrite=True)

        del df_all_pol


if __name__ == "__main__":
    start_date = '2022-07-10 00:00:00'
    end_date = '2022-07-11 00:00:00'

    job = DataProcessingJob(start_date, end_date)
    job.run()
