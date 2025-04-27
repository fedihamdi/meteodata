import logging
import os

import geocoder
import pandas as pd
from django.core.cache import cache

logger_me = logging.getLogger(__name__)


def filter_data_user_position(only_data=False):
    if not cache.get("my_data_key"):
        path = os.path.join(
            os.getcwd(),
            "data_nc",
            "data_file_20231116.parquet",
        )
        df = pd.read_parquet(path, engine="pyarrow")  # pd.read_csv(path)#
        geocoder.ip("me")
        # if g.latlng is None :
        user_latitude, user_longitude = [
            48.8534,
            2.4488
        ]  # montreuil:[48.8534, 2.4488] # Boul: 48.821216,2.233681,
        # else :
        # user_latitude, user_longitude = g.latlng
        filtered_df = df[
            (round(df["latitude"]) == round(user_latitude))
            & (round(df["longitude"]) == round(user_longitude))
        ]
        pollen_estimated = round(filtered_df["average_pollen_concentration"].mean(), 2)
        if pd.isna(pollen_estimated):
            pollen_estimated = 0
            filtered_df["average_pollen_concentration"].fillna(0, inplace=True)
        else:
            logger_me.info(
                f"estimated pollen concentration is available {pollen_estimated}"
            )
        cache.set("my_data_key", df, 3600)
        cache.set("my_data_key", filtered_df, 3600)
    else:
        df = cache.get("my_data_key")
        filtered_df = df

    if only_data:
        return [filtered_df, user_latitude, user_longitude, pollen_estimated]
    else:
        return filtered_df
