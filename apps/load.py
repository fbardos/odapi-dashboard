import datetime as dt
import io
import logging
import os
from typing import Literal

import geopandas as gpd
import pandas as pd
import pyarrow.parquet as pq
import requests
import streamlit as st
from dotenv import load_dotenv
from shapely import wkb

load_dotenv()

DEFAULT_CACHE_DURATION = 60 * 60 * 24  # 24 hours


class OdapiLoadException(Exception):
    pass


class OdapiWrapper:
    BASE_URL = os.getenv('ODAPI__BASE_URL', 'https://odapi.bardos.dev')

    def url_indicators_polg(self, format: Literal['json', 'txt']) -> str:
        match format:
            case 'json':
                return f'{self.BASE_URL}/indicators/polg'
            case 'txt':
                return f'{self.BASE_URL}/indicators/polg/txt'

    def url_municipalities_parquet(
        self, format: Literal['json', 'csv', 'xlsx', 'parquet'], year: int
    ) -> str:
        if format == 'json':
            return f'{self.BASE_URL}/municipalities/{year}'
        else:
            return f'{self.BASE_URL}/municipalities/{year}/{format}'

    def url_indicator_polg(
        self,
        indicator_id: int,
        format: Literal['json', 'csv', 'xlsx', 'parquet'],
        join_indicator: Literal['true', 'false'] = 'true',
        join_geo: Literal['true', 'false'] = 'true',
        geometry_mode: Literal[
            'point',
            'border',
            'border_simple_50_meter',
            'border_simple_100_meter',
            'border_simple_500_meter',
        ] = 'border_simple_500_meter',
    ) -> str:
        if format == 'json':
            return (
                f'{self.BASE_URL}/indicator/polg/{indicator_id}'
                f'?join_indicator={join_indicator}&join_geo={join_geo}&geometry_mode={geometry_mode}'
            )
        else:
            return (
                f'{self.BASE_URL}/indicator/polg/{indicator_id}/{format}'
                f'?join_indicator={join_indicator}&join_geo={join_geo}&geometry_mode={geometry_mode}'
            )


@st.cache_data(ttl=DEFAULT_CACHE_DURATION)
def load_indicator(sel_indicator_id: int) -> pd.DataFrame:
    url = OdapiWrapper().url_indicator_polg(sel_indicator_id, 'parquet')
    try:
        logging.debug(f'Loading indicator data from {url}')
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        raise OdapiLoadException(
            f'Error loading indicator data for indicator {sel_indicator_id}.'
        )
    logging.debug(f'Load buffer from ODAPI response.')
    buffer = io.BytesIO(response.content)
    logging.debug(f'Reading into pyarrow table.')
    table = pq.read_table(buffer)
    logging.debug(f'Converting to pandas DataFrame.')
    df = table.to_pandas()
    logging.debug(f'Transform geometry column from WKB to Shapely geometries.')
    df['geometry'] = df['geometry'].apply(wkb.loads)
    logging.debug(f'Generate GeoDataFrame from DataFrame.')
    gdf = gpd.GeoDataFrame(df, geometry='geometry').sort_values('period_ref')
    return gdf


@st.cache_data(ttl=DEFAULT_CACHE_DURATION)
def load_indicators() -> dict:
    url = OdapiWrapper().url_indicators_polg('json')
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        raise OdapiLoadException('Error loading indicators data.')
    return response.json()


@st.cache_data(ttl=DEFAULT_CACHE_DURATION)
def load_municipalities() -> pd.DataFrame:
    year = dt.datetime.now().year - 1
    url = OdapiWrapper().url_municipalities_parquet('parquet', year)
    return pd.read_parquet(url)
