import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")


@st.cache_data
def load_data(url: str, columns=None) -> pd.DataFrame:
    return pd.read_csv(url, sep=";", header=0, names=columns)


df = load_data(
    "https://opendata-files.sozialversicherung.at/sari/SARI_Wohnregion_Patient_v202307.csv",
    columns=[
        "weeknr_year",
        "region",
        "sex",
        "age_group",
        "station",
        "covid",
        "influenza",
        "rsv",
        "other",
        "admission",
        "population",
    ],
)

df["age_group"] = df["age_group"].replace({"5 - 14": "05 - 14"})
df2 = (
    df.groupby(["weeknr_year", "age_group"])
    .aggregate(
        {
            "covid": "sum",
            "influenza": "sum",
            "rsv": "sum",
            "other": "sum",
            "population": "max",
        }
    )
    .reset_index()
)

df2["total_diseases"] = df2[["covid", "influenza", "rsv", "other"]].sum(axis=1)
df2["real_date"] = pd.to_datetime(df2["weeknr_year"] + "-1", format="%W. KW %Y-%w")

df_to_display = df2[["real_date", "age_group", "total_diseases"]]

chart = (
    alt.Chart(df_to_display)
    .mark_line(point=True)
    .encode(
        x=alt.X("real_date:T").axis(format="%Y %B", labelAngle=-90),
        y="total_diseases",
        color="age_group",
    )
    .properties(width=1000, height=500)
)

st.title("Anzahl der Erkrankungen pro Altersgruppen")
st.altair_chart(chart, use_container_width=True)

df_kh = load_data(
    "https://opendata-files.sozialversicherung.at/sari/SARI_Region_Krankenanstalt_v202307.csv?q=now"
)

df_kh_2 = df_kh.groupby(["KW", "BUNDESLAND"]).aggregate(
    {
        "COVID": "sum",
        "INFLUENZA": "sum",
        "RSV": "sum",
        "SONSTIGE": "sum",
        "AUFNAHMEN": "sum",
    }
).reset_index()

df_kh_2['real_date'] = pd.to_datetime(df_kh_2['KW'] + '-1', format='%W. KW %Y-%w')

chart_kw = (
    alt.Chart(df_kh_2[['real_date', 'BUNDESLAND', 'AUFNAHMEN']])
    .mark_line(point=True)
    .encode(
        x=alt.X("real_date:T").axis(format="%Y %B", labelAngle=-90),
        y="AUFNAHMEN",
        color="BUNDESLAND",
    )
    .properties(width=1000, height=500)
)

st.title('Anzahl der Aufnahmen pro Bundesland')
st.altair_chart(chart_kw, use_container_width=True)

