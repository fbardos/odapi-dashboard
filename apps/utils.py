from typing import Tuple

import pandas as pd
import plotly.express as px


def get_topic_lvl(indicators: dict, indicator_id: int, lvl: int) -> str:
    """
    Get the topic level for the given indicator ID and level.
    """
    topic = next(
        i[f'topic_{lvl}'] for i in indicators if i['indicator_id'] == indicator_id
    )
    if topic is None:
        return '-'
    else:
        return topic


def _get_min_max_quantiles(
    df: pd.DataFrame, col_name: str = 'indicator_value_numeric'
) -> Tuple[float, float]:
    """
    Get the min and max quantiles of the specified column in the DataFrame.
    """
    _min = df[col_name].quantile(0.05)
    _max = df[col_name].quantile(0.95)
    assert isinstance(_min, float)
    assert isinstance(_max, float)
    return _min, _max


def decide_range_color(df: pd.DataFrame, col_name: str = 'indicator_value_numeric'):
    """
    Decide the range color based on the data.
    """
    _min, _max = _get_min_max_quantiles(df, col_name)
    if _min < 0:
        # _min = df[col_name].min()
        # _max = df[col_name].max()
        # assert isinstance(_min, float)
        # assert isinstance(_max, float)
        max_abs = max(abs(_min), abs(_max))
        return [-max_abs, max_abs]
    else:
        return [0, _max]


def decide_colorscale(df: pd.DataFrame, col_name: str = 'indicator_value_numeric'):
    """
    Decide the colorscale based on the data.
    """
    _min, _max = _get_min_max_quantiles(df, col_name)
    if _min < 0:
        return [  # Magma
            (0.0001, '#000004'),
            (0.0300, '#180f3d'),
            (0.1000, '#440f76'),
            (0.2000, '#721f81'),
            (1.0000, '#feca8d'),
        ]
        # return px.colors.sequential.RdBu
        # return [
        #     (0.0, 'rgb(255, 152, 183)'),
        #     (0.1, 'rgb(231,  77,  96)'),
        #     (0.2, 'rgb(178,  60,  41)'),
        #     (0.3, 'rgb(125,  46,  11)'),
        #     (0.4, 'rgb( 56,  22,   2)'),
        #     (0.5, 'rgb(  8,   8,   8)'),
        #     (0.6, 'rgb( 15,  35,  46)'),
        #     (0.7, 'rgb( 33,  84, 109)'),
        #     (0.8, 'rgb( 60, 140, 188)'),
        #     (0.9, 'rgb( 83, 152, 222)'),
        #     (1.0, 'rgb(158, 201, 250)'),
        # ]
    else:
        # return px.colors.sequential.Turbo
        # return px.colors.sequential.Inferno
        # return px.colors.sequential.Magma
        return px.colors.sequential.Viridis
        # return [  # Magma
        #     (0.0001, '#000004'),
        #     (0.0300, '#180f3d'),
        #     (0.1000, '#440f76'),
        #     (0.2000, '#721f81'),
        #     (1.0000, '#feca8d'),
        # ]
