import pandas as pd


class Indicator:

    @classmethod
    def indicator_df_info(
        cls, indicators: dict, sel_indicator_id: int, df: pd.DataFrame
    ):
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
        yield f"### Data preview"
        yield "\n"
        yield df.head(20)
