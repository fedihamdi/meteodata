import logging
from django.core.cache import cache
import pandas as pd
import os
import geocoder
logger_me = logging.getLogger(__name__)
logger_me.setLevel(logging.DEBUG)
def filter_data_user_position(ony_data=False):
    df = None
    filtered_df = None
    if not cache.get('my_data_key'):
        path = os.path.join(os.getcwd()[:-20], 'data_file_2022-07-10.csv')
        df = pd.read_csv(path)
        g = geocoder.ip('me')
        user_latitude, user_longitude = g.latlng
        filtered_df = df[
            (round(df['latitude']) == round(user_latitude)) & (round(df['longitude']) == round(user_longitude))]
        pollen_estimated = filtered_df.average_pollen_concentration.mean()
        cache.set('my_data_key', df, 3600)
        cache.set('my_data_key', filtered_df, 3600)
    if df is None or filtered_df is None:
        df = cache.get('my_data_key')
    if ony_data:

        try:
            return [filtered_df, user_latitude, user_longitude]
        except :
            logger_me.info([filtered_df, user_latitude, user_longitude, pollen_estimated])
            logger_me.warning("This is failing 1")
    else:
        logger_me.info("This is failing 2")
        return filtered_df