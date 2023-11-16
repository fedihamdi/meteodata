import logging
import os
import re
from datetime import datetime

import cdsapi
import xarray as xr
from dotenv import load_dotenv  # only secure en dev à supprimer en prod

load_dotenv()  # idem pour supprimer
logger = logging.getLogger(__name__)


def is_valid_date_format(date_string):
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    if re.match(date_pattern, date_string) is not None:
        return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    else:
        try:
            return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").strftime(
                "%Y-%m-%d"
            )
        except Exception as e:
            logger.warning(
                f"The date {date_string} you are entering does not respect the for format"
                f" YYYY-MM-DD HH:MM:SS please see the below error for more details --- \n"
                f"{e}"
            )


class CAMSDataRetriever:
    def __init__(
        self,
        variables=[
            "alder_pollen",
            "ammonia",
            "carbon_monoxide",
            "dust",
            "formaldehyde",
            "glyoxal",
            "nitrogen_dioxide",
            "nitrogen_monoxide",
            "non_methane_vocs",
            "ozone",
            "particulate_matter_10um",
            "particulate_matter_2.5um",
            "peroxyacyl_nitrates",
            "pm10_wildfires",
            "residential_elementary_carbon",
            "secondary_inorganic_aerosol",
            "sulphur_dioxide",
            "total_elementary_carbon",
        ],
        start_date="2023-10-07",
        end_date="2023-10-09",
        type="analysis",
    ):
        """
        Initializes the CAMSDataRetriever class with default parameters.
        These parameters can be customized for data retrieval.

        Attributes:
            self.c: cdsapi.Client instance for data retrieval.
            self.variables: List of variables to be retrieved.
            self.model: Data model name (default: 'ensemble').
            self.start_date: Start date for data retrieval in the format 'YYYY-MM-DD'.
            self.end_date: End date for data retrieval in the format 'YYYY-MM-DD'.
            self.format: Data format (default: 'netcdf').
            self.level: Data level (default: '1000').
            self.type: Data type (default: 'analysis').
            self.time: Data time (default: '12:00').
            self.leadtime_hour: Leadtime hour (default: '0').
        """
        if type not in ["analysis", "forecast"]:
            raise ValueError("Type must be 'analysis' or 'forecast'")
        if type == "analysis":
            level = "1000"
            time = "12:00"
        else:
            level = "0"
            time = "00:00"
        CAMS_URL = os.environ.get("CDSAPI_URL_CAMS")  # env vars pour la cnx API CAMS
        CAMS_KEY = os.environ.get("CDSAPI_KEY_CAMS")
        self.c = cdsapi.Client(url=CAMS_URL, key=CAMS_KEY)
        self.variables = variables
        self.model = "ensemble"
        self.start_date = is_valid_date_format(start_date)
        self.end_date = is_valid_date_format(end_date)
        self.format = "netcdf"
        self.level = level
        self.type = type
        self.time = time
        self.leadtime_hour = "0"

    def retrieve_data(self, output_filename):
        """
        Retrieves CAMS data and saves it to the specified output file.

        Args:
            output_filename (str): The name of the output file to save the retrieved data.

        Returns:
            None
        """
        request_params = {
            "model": self.model,
            "date": f"{self.start_date}/{self.end_date}",
            "format": self.format,
            "variable": self.variables,
            "level": self.level,
            "type": self.type,
            "time": self.time,
            "leadtime_hour": self.leadtime_hour,
            "area": [49.88, 1.09, 48, 3.95],
        }
        self.c.retrieve(
            "cams-europe-air-quality-forecasts", request_params, output_filename
        )

    def open_dataset(self, filename):
        """
        Opens and returns a dataset from the specified filename.

        Args:
            filename (str): The name of the file containing the dataset.

        Returns:
            xr.Dataset: An xarray Dataset containing the retrieved data.
        """
        return xr.open_dataset(filename)

    def get_variable_descriptions(self, data):
        """
        Returns descriptions of variables in the dataset.

        Args:
            data (xr.Dataset): The dataset to extract variable descriptions from.

        Returns:
            dict: A dictionary of variable names mapped to their descriptions.
        """
        variable_descriptions = {}
        for var_name in data.variables.keys():
            try:
                variable_descriptions[var_name] = data[var_name].attrs["long_name"]
            except KeyError as e:
                variable_descriptions[var_name] = data[var_name].attrs["species"]
                logger.warning(f"Got this error {e}")
        return variable_descriptions
