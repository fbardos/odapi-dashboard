import pandas as pd
import plotly.express as px
import streamlit as st

from load import load_indicators
from load import load_municipalities
from utils import get_topic_lvl

##############################################################################
# SITE STRUCTURE #############################################################
##############################################################################
st.set_page_config(layout="wide")

indicators = load_indicators()
municipalities = load_municipalities()


st.title('ODAPI Explorer: Gemeinde-Portrait')
st.markdown(
    """
    Diese Webanwendung ermöglicht es, die Daten des [ODAPI (Open Data API)](https://odapi.bardos.dev) zu erkunden.
"""
)

tab_indicator, tab_portrait, tab_benchmark = st.tabs(
    ['Indikator', 'Portrait', 'Benchmark']
)

with tab_indicator:

    st.markdown(
        """
        Unter `Indikator` können alle Werte zu einem bestimmten Indikator auf Gemeindeebene abgerufen werden.
        """
    )


with tab_portrait:

    st.markdown(
        """
        Unter `Portrait` können alle Indikatoren zu einer bestimmten Gemeinde abgerufen werden.
        """
    )
    with st.container(border=True):

        def _sort_function(x):
            if x == 230:  # Winterthur as default
                return 0
            else:
                return x

        _municipality_options = municipalities['gemeinde_bfs_id'].tolist()
        _municipality_options.sort(key=_sort_function)

        sel_municipality_id = st.selectbox(
            'Auswahl Gemeinde',
            options=_municipality_options,
            index=0,
            format_func=lambda x: municipalities[
                municipalities['gemeinde_bfs_id'] == x
            ]['gemeinde_name'].values[0],
        )

    data_portrait = pd.read_parquet(
        f'https://odapi.bardos.dev/portrait/polg/{sel_municipality_id}/parquet?join_indicator=true'
    )
    data_hist = pd.read_parquet(f'http://localhost:8000/values/polg/parquet')

    unique_indicators = data_portrait['indicator_id'].unique().tolist()

    portrait_col1, portrait_col2 = st.columns(2)

    for idx, indicator_id in enumerate(unique_indicators):
        _indicator_name = data_portrait[data_portrait['indicator_id'] == indicator_id][
            'indicator_name'
        ].values[0]
        _indicator_unit = data_portrait[data_portrait['indicator_id'] == indicator_id][
            'indicator_unit'
        ].values[0]
        _indicator_descr = data_portrait[data_portrait['indicator_id'] == indicator_id][
            'indicator_description'
        ].values[0]
        _df = data_portrait[data_portrait['indicator_id'] == indicator_id]
        _df = _df.sort_values('period_ref')
        _df_hist = data_hist[data_hist['indicator_id'] == indicator_id]
        _latest_value = _df['indicator_value_numeric'].values[-1]
        _latest_year = _df['period_ref'].values[-1]
        _delta_pct = _df['indicator_value_numeric'].pct_change().values[-1]
        _sources = _df['source'].unique().tolist()
        _df_hist['rank'] = (
            _df_hist[['indicator_id', 'indicator_value_numeric']]
            .groupby('indicator_id')['indicator_value_numeric']
            .rank(ascending=False)
        )
        print(_df_hist[_df_hist['geo_value'] == 230])

        if idx % 2 == 0:
            portrait_col = portrait_col1
        else:
            portrait_col = portrait_col2

        with portrait_col.container(border=True):

            st.subheader(f"{_indicator_name} | {_indicator_unit}")
            col1, col2, col3 = st.columns([5, 2, 1])
            col1.text(_indicator_descr)
            col1.markdown(
                f":blue-badge[:material/counter_1: {get_topic_lvl(indicators, indicator_id, 1)}] "
                f":blue-badge[:material/counter_2: {get_topic_lvl(indicators, indicator_id, 2)}] "
                f":blue-badge[:material/counter_3: {get_topic_lvl(indicators, indicator_id, 3)}] "
                f":blue-badge[:material/counter_4: {get_topic_lvl(indicators, indicator_id, 4)}] "
            )
            col2.metric(
                label=f'Jahr {_latest_year.astype("datetime64[Y]").astype(int) + 1970}',
                value=_latest_value,
                delta=f'{_delta_pct:.2f} %',
            )
            col3.metric(
                label=f'Platz',
                value=f"{_df_hist[(_df_hist['geo_value'] == sel_municipality_id) & (_df_hist['indicator_id'] == indicator_id)]['rank'].values[0]:.0f}",
                help=f"von {len(_df_hist[_df_hist['indicator_id'] == indicator_id]):.0f} Gemeinden",
            )

            fig_line = px.line(
                _df,
                x='period_ref',
                y='indicator_value_numeric',
                title=_indicator_name,
                labels={
                    'period_ref': 'Jahr',
                    'indicator_value_numeric': _indicator_unit,
                },
                height=400,
            )
            fig_line.update_layout(
                yaxis_title=None, xaxis_fixedrange=True, yaxis_fixedrange=True
            )
            st.plotly_chart(fig_line, key=f'line_{indicator_id}')

            fig_hist = px.histogram(
                _df_hist,
                title='Histogramm (aktuellstes Jahr)',
                x='indicator_value_numeric',
                nbins=50,
                height=300,
                labels={
                    'count': 'Anzahl',
                    'indicator_value_numeric': _indicator_unit,
                },
            )
            fig_hist.add_vline(
                x=_latest_value,
                line_dash='dash',
                line_color='#AD49E1',
                annotation_text=f'  {municipalities[municipalities["gemeinde_bfs_id"] == sel_municipality_id]["gemeinde_name"].values[0]}  ',
            )
            fig_hist.update_layout(
                yaxis_title=None, xaxis_fixedrange=True, yaxis_fixedrange=True
            )
            st.plotly_chart(fig_hist, key=f'hist_{indicator_id}')

            st.markdown(
                f"""
                Quellen: {", ".join(_sources)}\n
                Download data as
                [CSV](https://odapi.bardos.dev/indicator/polg/{indicator_id}/csv?geo_value={sel_municipality_id}&join_indicator=true&expand_all_groups=true),
                [Excel](https://odapi.bardos.dev/indicator/polg/{indicator_id}/xlsx?geo_value={sel_municipality_id}&join_indicator=true&expand_all_groups=true),
                [GeoJSON](https://odapi.bardos.dev/indicator/polg/{indicator_id}?geo_value={sel_municipality_id}&join_indicator=true&expand_all_groups=true),
                [GeoParquet](https://odapi.bardos.dev/indicator/polg/{indicator_id}/parquet?geo_value={sel_municipality_id}&join_indicator=true&expand_all_groups=true)
            """
            )
            # st.write(_df[['period_ref', 'indicator_value_numeric']])
            # st.plotly_chart(
            #     px.line(
            #         _df,
            #         x='period_ref',
            #         y='indicator_value_numeric',
            #         title=data_portrait[data_portrait['indicator_id'] == indicator_id][
            #             'indicator_name'
            #         ].values[0],
            #     )
            # )

    # st.write(data_portrait)

with tab_benchmark:

    st.markdown(
        """
        Coming soon.
        """
    )
