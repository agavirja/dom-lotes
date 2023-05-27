import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import altair as alt
import plotly.graph_objects as go
import plotly.express as px

import copy
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from bs4 import BeautifulSoup

from html_scripts import table2,boxkpi

from shapely import wkt
from sqlalchemy import create_engine 

# streamlit run D:\Dropbox\Empresa\stramlitAPP\lotes\main.py
# pipreqs --encoding utf-8 "D:\Dropbox\Empresa\stramlitAPP\lotes\online"

st.set_page_config(layout="wide",initial_sidebar_state="expanded")

user     = st.secrets["user"]
password = st.secrets["password"]
host     = st.secrets["host"]
schema   = st.secrets["schema"]
engine   = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')

@st.experimental_memo
def getpolygon():
    data   = pd.read_sql_query("""SELECT ST_AsText(geometry) as wkt FROM lotes.dom_geometry_barrios_piloto1"""  , engine)
    data['wkt'] = data['wkt'].apply(lambda x: wkt.loads(x))
    return data


data = getpolygon()
st.dataframe(data)