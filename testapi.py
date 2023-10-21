import cdsapi
import pandas
import xarray as xr

c = cdsapi.Client()
variables_ = ["temperature", "total_precipitation", "relative humidity"]

c.retrieve(
    "reanalysis-era5-pressure-levels",
    {
        "variable": variables_,
        "pressure_level": "1000",
        "product_type": "reanalysis",
        "year": "2022",
        "month": "07",
        "day": [str(i) for i in range(10, 32)],
        "time": "12:00",
        "format": "netcdf",
    },
    "random_data.nc",
)

c.retrieve(
    "reanalysis-era5-single-levels",
    {
        "variable": variables_,
        "pressure_level": "1000",
        "product_type": "reanalysis",
        "year": "2022",
        "month": "07",
        "day": [str(i) for i in range(10, 32)],
        "time": "12:00",
        "format": "netcdf",
    },
    "random_data2.nc",
)


data = xr.open_dataset("random_data.nc")
data2 = xr.open_dataset("random_data2.nc")

df = data.to_dataframe().reset_index()
df2 = data2.to_dataframe().reset_index()

df_merged = pandas.merge(df, df2, on=["longitude", "latitude", "time"], how="inner")

c.close()
