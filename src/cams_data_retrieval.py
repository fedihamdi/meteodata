import cdsapi
import xarray as xr

class CAMSDataRetriever:
    def __init__(self):
        self.c = cdsapi.Client()
        self.variables = [
            'alder_pollen', 'ammonia', 'carbon_monoxide', 'dust',
            'formaldehyde', 'glyoxal', 'nitrogen_dioxide',
            'nitrogen_monoxide', 'non_methane_vocs', 'ozone',
            'particulate_matter_10um', 'particulate_matter_2.5um', 'peroxyacyl_nitrates',
            'pm10_wildfires', 'residential_elementary_carbon', 'secondary_inorganic_aerosol',
            'sulphur_dioxide', 'total_elementary_carbon',
        ]
        self.model = 'ensemble'
        self.date = '2023-10-07/2023-10-09'
        self.format = 'netcdf'
        self.level = '1000'
        self.type = 'analysis'
        self.time = '12:00'
        self.leadtime_hour = '0'

    def retrieve_data(self, output_filename):
        request_params = {
            'model': self.model,
            'date': self.date,
            'format': self.format,
            'variable': self.variables,
            'level': self.level,
            'type': self.type,
            'time': self.time,
            'leadtime_hour': self.leadtime_hour,
        }
        self.c.retrieve('cams-europe-air-quality-forecasts', request_params, output_filename)

    def open_dataset(self, filename):
        return xr.open_dataset(filename)

    def get_variable_descriptions(self, data):
        variable_descriptions = {}
        for var_name in data.variables.keys():
            try:
                variable_descriptions[var_name] = data[var_name].attrs['long_name']
            except KeyError as e:
                variable_descriptions[var_name] = data[var_name].attrs['species']
        return variable_descriptions