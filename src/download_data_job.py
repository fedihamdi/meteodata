from cams_data_retrieval import CAMSDataRetriever
from era5_data_retriever import ERA5DataRetriever
import multiprocessing
from datetime import date
import logging
import os
from azure.storage.blob import BlobClient
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)


def download_era5_data_th(output_filename, start_date, end_date):
    retriever = ERA5DataRetriever(start_date=start_date, end_date=end_date)
    retriever.retrieve_data(output_filename=output_filename)


def download_era5_data_p(output_filename, start_date, end_date):
    retriever = ERA5DataRetriever(start_date=start_date, end_date=end_date)
    retriever.retrieve_data(
        output_filename=output_filename, database="reanalysis-era5-single-levels"
    )


def download_cams_data_aq(output_filename, start_date, end_date):
    retriever = CAMSDataRetriever(start_date=start_date, end_date=end_date)
    retriever.retrieve_data(output_filename=output_filename)


def download_cams_data_pol(output_filename, start_date, end_date):
    retriever = CAMSDataRetriever(
        start_date=start_date,
        end_date=end_date,
        type="forecast",
        variables=[
            "alder_pollen",
            "birch_pollen",
            "grass_pollen",
            "mugwort_pollen",
            "olive_pollen",
            "ragweed_pollen",
        ],
    )
    retriever.retrieve_data(output_filename=output_filename)


def main():
    start_date = "2022-05-01 00:00:00"
    end_date = "2022-10-01 00:00:00"
    today = str(date.today()).replace("-", "")

    era5_filename_th = f"era5_data_temp_humidity_{today}.nc"
    era5_filename_p = f"era5_data_precip_{today}.nc"
    cams_filename_aq = f"cams_data_air_quality_{today}.nc"
    cams_filename_pol = f"cams_data_pollen_{today}.nc"

    # Create separate processes for downloading ERA5 and CAMS data
    era5_process_th = multiprocessing.Process(
        target=download_era5_data_th, args=(era5_filename_th, start_date, end_date)
    )
    era5_process_precip = multiprocessing.Process(
        target=download_era5_data_p, args=(era5_filename_p, start_date, end_date)
    )

    cams_process_aq = multiprocessing.Process(
        target=download_cams_data_aq, args=(cams_filename_aq, start_date, end_date)
    )
    cams_process_pol = multiprocessing.Process(
        target=download_cams_data_pol, args=(cams_filename_pol, start_date, end_date)
    )

    era5_process_th.start()
    era5_process_precip.start()

    cams_process_aq.start()
    cams_process_pol.start()

    era5_process_th.join()
    era5_process_precip.join()

    cams_process_aq.join()
    cams_process_pol.join()

    local_files = [
        era5_filename_th,
        era5_filename_p,
        cams_filename_aq,
        cams_filename_pol,
    ]
    logger.info("Starting migration to blob")

    connectionString = os.environ.get("BLOB_CONNECTION_STRING")
    containerName = "output"

    for local_file in local_files:
        local_file_path = os.path.abspath(local_file)

        # Define the name of the blob in the Azure Blob Storage container
        output_blob_name = os.path.basename(local_file_path)

        logger.info(f"file is in {output_blob_name}")
        blob = BlobClient.from_connection_string(
            conn_str=connectionString,
            container_name=containerName,
            blob_name=output_blob_name,
        )

        # Upload the local file to Azure Blob Storage
        with open(local_file_path, "rb") as data:
            blob.upload_blob(data, overwrite=True)
    blob = BlobClient.from_connection_string(
        conn_str=connectionString,
        container_name=containerName,
        blob_name="requirements.txt",
    )

    # Upload the local file to Azure Blob Storage
    with open("requirements.txt", "rb") as data:
        blob.upload_blob(data, overwrite=True)
    logger.info("Process status: Success")


if __name__ == "__main__":
    main()
    logger.info("Process status: Success")
