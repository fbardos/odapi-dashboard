import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from load import OdapiWrapper
from utils import decide_colorscale
from utils import decide_range_color


class BaseSite:
    pass


class SiteIndicator(BaseSite):

    @classmethod
    def df_info(cls, indicators: dict, sel_indicator_id: int, df: pd.DataFrame):
        _indicator = next(
            i for i in indicators if i['indicator_id'] == sel_indicator_id
        )
        yield f"* Indicator ID{_indicator['indicator_id']}"
        yield "\n"
        yield f"* Indicator Name: {_indicator['indicator_name']}"
        yield "\n"
        yield f"* Topic 1: {_indicator['topic_1']}"
        yield "\n"
        yield f"* Topic 2: {_indicator['topic_2']}"
        yield "\n"
        yield f"* Topic 3: {_indicator['topic_3']}"
        yield "\n"
        yield f"* Topic 4: {_indicator['topic_4']}"
        yield "\n"
        yield f"* Data Rows: {len(df.index)}"
        yield "\n"
        yield f"* Data Columns: {len(df.columns)}"
        yield "\n"
        yield f"* Quellen: {', '.join(df['source'].unique())}"
        yield "\n"
        yield f"### Data preview"
        yield "\n"
        yield df.head(20)

    @classmethod
    def data_download_urls(cls, sel_indicator_id: int):
        _url_json = OdapiWrapper().url_indicator_polg(sel_indicator_id, 'json')
        _url_csv = OdapiWrapper().url_indicator_polg(sel_indicator_id, 'csv')
        _url_xlsx = OdapiWrapper().url_indicator_polg(sel_indicator_id, 'xlsx')
        _url_parquet = OdapiWrapper().url_indicator_polg(sel_indicator_id, 'parquet')
        yield f"### Download Daten"
        yield "\n"
        yield f"* als GeoJSON: {_url_json}"
        yield "\n"
        yield f"* als CSV: {_url_csv}"
        yield "\n"
        yield f"* als Excel: {_url_xlsx}"
        yield "\n"
        yield f"* als GeoParquet-File: {_url_parquet}"

    @classmethod
    def df_leader_table_by_year(
        cls, df: pd.DataFrame, period_ref: str, ascending: bool = True
    ) -> pd.DataFrame:
        _df = (
            df[df['period_ref'] == period_ref]
            .sort_values('indicator_value_numeric', ascending=ascending)
            .head(5)
        )
        return _df[
            ['geo_name', 'bezirk_name', 'kanton_name', 'indicator_value_numeric']
        ]

    @classmethod
    def df_other(
        cls, df: pd.DataFrame, df_other: pd.DataFrame, hist_year: str
    ) -> pd.DataFrame:
        df_other = df_other.copy()
        df_other = df_other[df_other['period_ref'] == hist_year][
            ['geo_value', 'indicator_value_numeric', 'indicator_unit']
        ].rename(
            columns={
                'indicator_value_numeric': 'other_value',
                'indicator_unit': 'other_indicator_unit',
            }
        )
        df = df.merge(how='inner', right=df_other, on='geo_value')
        return df

    @classmethod
    def fig_map_by_year(cls, df: pd.DataFrame, year: int) -> go.Figure:
        _df = df[df['period_ref'] == year]
        _fig_map = px.choropleth_mapbox(
            _df,
            geojson=_df.geometry,
            locations=_df.index,
            color='indicator_value_numeric',
            mapbox_style='carto-positron',
            opacity=0.5,
            zoom=7.4,
            center=dict(lat=46.8, lon=8.4),
            color_continuous_scale=decide_colorscale(_df),
            range_color=decide_range_color(_df),
            hover_data={
                'geo_name': True,
                'bezirk_name': True,
                'kanton_name': True,
                'indicator_unit': True,
            },
            labels={'indicator_value_numeric': _df['indicator_unit'].iloc[0][:30]},
        )
        _fig_map.update_traces(
            hovertemplate=(
                'Gemeinde <b>%{customdata[0]}</b><br>'
                'Wert <b>%{z}</b> %{customdata[3]}<br><br>'
                'Bezirk %{customdata[1]} <br>'
                'Kanton %{customdata[2]} <br>'
            ),
        )
        _fig_map.update_layout(
            geo=dict(fitbounds="locations", visible=False),
            margin=dict(l=0, r=0, b=0, t=0, pad=4),
            height=700,
            coloraxis_colorbar_orientation='h',
            coloraxis_colorbar_yanchor='bottom',
            coloraxis_colorbar_y=0,
            coloraxis_colorbar_xanchor='right',
            coloraxis_colorbar_x=0.98,
            coloraxis_colorbar_len=0.35,
        )
        return _fig_map

    @classmethod
    def fig_boxplot_per_year(
        cls, df: pd.DataFrame, lower_period_ref: str, upper_period_ref: str
    ) -> go.Figure:
        _df = df.copy()
        _df = _df[_df['period_ref'].between(lower_period_ref, upper_period_ref)]
        fig = px.box(
            _df,
            x='period_ref',
            y='indicator_value_numeric',
            hover_data={
                'geo_name': True,
                'bezirk_name': True,
                'kanton_name': True,
                'indicator_unit': True,
            },
        )
        fig.update_traces(
            hovertemplate=(
                'Gemeinde <b>%{customdata[0]}</b><br>'
                'Wert <b>%{y}</b> %{customdata[3]}<br><br>'
                'Bezirk %{customdata[1]} <br>'
                'Kanton %{customdata[2]} <br>'
            )
        )
        fig.update_layout(
            xaxis_title='Jahr',
            yaxis_title='Wert',
        )
        fig.update_traces(quartilemethod="exclusive", marker_size=2)
        return fig

    @classmethod
    def fig_heatmap_per_year(
        cls, df: pd.DataFrame, lower_period_ref: str, upper_period_ref: str
    ) -> go.Figure:
        _df = df.copy()
        _df = _df[_df['period_ref'].between(lower_period_ref, upper_period_ref)]
        assert isinstance(_df, pd.DataFrame)
        fig = px.density_heatmap(
            _df,
            x='period_ref',
            y='indicator_value_numeric',
            # facet_col_spacing=0.05,
            # log_y=True,
            nbinsx=_df['period_ref'].nunique(),
            nbinsy=50,
            height=300,
        )
        fig.update_layout(
            xaxis_title='Jahr',
            yaxis_title='Wert',
        )
        return fig

    @classmethod
    def fig_compare_with_other_indicator(
        cls,
        df: pd.DataFrame,
        indicators: dict,
        sel_indicator_id: int,
        sel_other_indicator_id: int,
    ) -> go.Figure:
        fig = px.scatter(
            df,
            x='indicator_value_numeric',
            y='other_value',
            labels={
                'indicator_value_numeric': [
                    f"{i['indicator_name']} ({i['indicator_unit']})"
                    for i in indicators
                    if i['indicator_id'] == sel_indicator_id
                ][0],
                'other_value': [
                    f"{i['indicator_name']} ({i['indicator_unit']})"
                    for i in indicators
                    if i['indicator_id'] == sel_other_indicator_id
                ][0],
            },
            trendline='lowess',
            trendline_color_override='#F97A00',
            hover_data={
                'geo_name': True,
                'bezirk_name': True,
                'kanton_name': True,
                'indicator_unit': True,
                'other_indicator_unit': True,
            },
        )
        fig.update_traces(
            hovertemplate=(
                'Gemeinde <b>%{customdata[0]}</b><br>'
                'Wert X: <b>%{x}</b> %{customdata[3]}<br>'
                'Wert Y: <b>%{y}</b> %{customdata[4]}<br><br>'
                'Bezirk %{customdata[1]} <br>'
                'Kanton %{customdata[2]} <br>'
            )
        )
        return fig

    @classmethod
    def fig_hist_by_year(cls, df: pd.DataFrame, year: int) -> go.Figure:
        fig = px.histogram(
            df[df['period_ref'] == year],
            x='indicator_value_numeric',
            height=300,
            labels={
                'indicator_value_numeric': df['indicator_unit'].iloc[0][:30],
            },
        )
        return fig

    @classmethod
    def fig_change_over_time(
        cls, df: pd.DataFrame, lower_period_ref: str, upper_period_ref: str
    ) -> go.Figure:
        _col_name_change = 'Veränderung (%)'
        _df_sorted = df.copy()
        _df_sorted = _df_sorted.sort_values(['geo_value', 'period_ref'])

        _df = _df_sorted[
            _df_sorted['period_ref'].isin([lower_period_ref, upper_period_ref])
        ]
        _df[_col_name_change] = (
            _df.groupby('geo_value')['indicator_value_numeric'].pct_change() * 100
        )
        _fig_map = px.choropleth_mapbox(
            _df,
            geojson=_df.geometry,
            locations=_df.index,
            color='Veränderung (%)',
            mapbox_style='carto-positron',
            opacity=0.5,
            zoom=7.4,
            center=dict(lat=46.8, lon=8.4),
            color_continuous_scale=decide_colorscale(_df, _col_name_change),
            range_color=decide_range_color(_df, _col_name_change),
            hover_data={
                'geo_name': True,
                'bezirk_name': True,
                'kanton_name': True,
                'indicator_unit': True,
            },
        )
        _fig_map.update_traces(
            hovertemplate=(
                'Gemeinde <b>%{customdata[0]}</b><br>'
                f'Veränderung zwischen <b>{lower_period_ref}</b> und <b>{upper_period_ref}</b>: '
                '<b>%{z:.2f}</b> %<br><br>'
                'Bezirk %{customdata[1]} <br>'
                'Kanton %{customdata[2]} <br>'
            )
        )
        _fig_map.update_layout(
            geo=dict(fitbounds="locations", visible=False),
            margin=dict(l=0, r=0, b=0, t=0, pad=4),
            height=700,
            coloraxis_colorbar_orientation='h',
            coloraxis_colorbar_yanchor='bottom',
            coloraxis_colorbar_y=0,
            coloraxis_colorbar_xanchor='right',
            coloraxis_colorbar_x=0.98,
            coloraxis_colorbar_len=0.35,
        )
        return _fig_map
