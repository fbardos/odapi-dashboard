import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from components import SiteIndicator
from load import load_indicator
from load import load_indicators
from load import load_municipalities
from utils import get_topic_lvl

load_dotenv()

st.set_page_config(page_title='ODAPI Explorer: Indikator', layout="wide")

indicators = load_indicators()
municipalities = load_municipalities()


# APP ########################################################################
st.title('ODAPI Explorer: Indikator')
st.markdown(
    f"""
    Diese Webanwendung ermöglicht es, die Daten des [ODAPI (Open Data API)](https://odapi.bardos.dev) zu erkunden.
    Der Source Code dieser Anwendung ist auf [Github](http://github.com/fbardos) zu finden.

    Für die Visualisierung der ODAPI-Daten existieren weitere Dashboards:
    * [ODAPI Explorer: Gemeinde-Portrait]({os.getenv('DASH__URL_PORTRAIT')})
    * Coming soon: ODAPI Explorer: Gemeinde-Benchmark
"""
)

st.warning(
    """
    **Alpha Version**

    Diese Anwendung wird aktuell noch entwickelt und kann sich jederzeit ändern und Fehler enthalten.
    Dies gilt ebenso für die zugrundeliegende API.
"""
)

tab_indicator, tab_data = st.tabs(['Indikator', 'Daten'])

# VISUALS: INDIKATOR #########################################################
with tab_indicator:

    st.markdown(
        """
        Unter `Indikator` können alle Werte zu einem bestimmten Indikator auf Gemeindeebene abgerufen werden.
        """
    )

    # NAVIGATION #################################################################
    with st.container(border=True):
        sel_indicator_id = int(
            st.selectbox(
                'Auswahl Indikator',
                options=[i['indicator_id'] for i in indicators],
                index=125,  # Median reines Äquivalenzeinkommen
                format_func=lambda x: [
                    f"{i['indicator_name']} | {i['topic_1']} >> {i['topic_2']} >> {i['topic_3']} >> {i['topic_4']} | {i['indicator_unit']}"
                    for i in indicators
                    if i['indicator_id'] == x
                ][0],
            )
        )

    st.markdown(
        f":blue-badge[:material/counter_1: {get_topic_lvl(indicators, sel_indicator_id, 1)}] "
        f":blue-badge[:material/counter_2: {get_topic_lvl(indicators, sel_indicator_id, 2)}] "
        f":blue-badge[:material/counter_3: {get_topic_lvl(indicators, sel_indicator_id, 3)}] "
        f":blue-badge[:material/counter_4: {get_topic_lvl(indicators, sel_indicator_id, 4)}] "
    )

    df = load_indicator(sel_indicator_id)
    min_period_ref = df['period_ref'].min()
    max_period_ref = df['period_ref'].max()

    # SINGLE YEAR ################################################################
    with st.container(border=False):
        st.subheader('Für ausgewähltes Jahr')
        with st.container(border=True):
            hist_year = st.select_slider(
                'Jahr auswählen',
                options=df['period_ref'].unique(),
                value=max_period_ref,
            )

        st.plotly_chart(SiteIndicator.fig_map_by_year(df, hist_year))

        c_data = st.container()
        c_data_col_1, c_data_col_2 = st.columns(2)

        c_data_col_1.subheader('Top 5')
        c_data_col_1.dataframe(
            SiteIndicator.df_leader_table_by_year(df, hist_year, ascending=False),
            hide_index=True,
        )
        c_data_col_2.subheader('Bottom 5')
        c_data_col_2.dataframe(
            SiteIndicator.df_leader_table_by_year(df, hist_year, ascending=True),
            hide_index=True,
        )

        st.plotly_chart(SiteIndicator.fig_hist_by_year(df, hist_year))

        st.subheader('Vergleich mit anderem Indikator')
        with st.container(border=True):
            sel_other_indicator_id = int(
                st.selectbox(
                    'Auswahl anderer Indikator',
                    options=[i['indicator_id'] for i in indicators],
                    index=72,  # Anteil E-Autos
                    format_func=lambda x: [
                        f"{i['indicator_name']} | {i['topic_1']} >> {i['topic_2']} >> {i['topic_3']} >> {i['topic_4']} | {i['indicator_unit']}"
                        for i in indicators
                        if i['indicator_id'] == x
                    ][0],
                )
            )

        df_other = load_indicator(sel_other_indicator_id)
        df_this = df[df['period_ref'] == hist_year]
        assert isinstance(df_this, pd.DataFrame)
        df_compare_sel = SiteIndicator.df_other(df_this, df_other, hist_year)
        if len(df_compare_sel.index) == 0:
            st.warning(
                "Keine Daten für den ausgewählten Indikator und das Jahr vorhanden."
            )
        else:
            st.markdown(
                'Trendlinie als `Locally Weighted Scatterplot Smoothing (LOWESS)`'
            )
            st.plotly_chart(
                SiteIndicator.fig_compare_with_other_indicator(
                    df_compare_sel, indicators, sel_indicator_id, sel_other_indicator_id
                )
            )

    # ALL YEARS ##################################################################
    with st.container(border=False):
        st.subheader('Alle Jahre')
        with st.container(border=True):
            sel_year_range_lower, sel_year_range_upper = st.select_slider(
                'Jahre auswählen',
                options=df['period_ref'].unique(),
                value=(min_period_ref, max_period_ref),
            )

        st.subheader('Veränderung über die Jahre')
        st.markdown(
            "Zeigt die Veränderung des Wertes zwischen dem ersten und letzten verfügbaren Jahr an. "
            "Veränderung in Prozent (%) gegenüber dem ersten verfügbaren Jahr. "
            "Leere Flächen deuten oft darauf hin, dass eine Gemeinde fusiniert wurde und deshalb nicht dargstellt werden kann. "
        )
        st.plotly_chart(
            SiteIndicator.fig_change_over_time(
                df, sel_year_range_lower, sel_year_range_upper
            )
        )

        st.subheader('Verteilung pro Jahr')
        st.markdown(
            "Zeigt einen Boxplot (inklusive Outlier) über die verschiedenen Jahre an. "
        )
        st.plotly_chart(
            SiteIndicator.fig_boxplot_per_year(
                df, sel_year_range_lower, sel_year_range_upper
            )
        )

        st.markdown(
            "Zeigt eine Heatmap der Verteilung der Werte über die verschiedenen Jahre an. "
        )
        st.plotly_chart(
            SiteIndicator.fig_heatmap_per_year(
                df, sel_year_range_lower, sel_year_range_upper
            )
        )


# DATA: INDIKATOR ############################################################
with tab_data:

    st.markdown(
        """
        Hier finden sich weiterführende Informationen zu den zugrundeliegenden Daten aus dem ODAPI.
        """
    )

    with st.container(border=True):
        st.subheader('Informationen zum Indikator')
        st.write_stream(SiteIndicator.df_info(indicators, sel_indicator_id, df))

    with st.container(border=True):
        st.subheader('Download Daten')
        st.write_stream(SiteIndicator.data_download_urls(sel_indicator_id))
