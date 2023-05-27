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
from shapely.geometry import mapping


import random
# streamlit run D:\Dropbox\Empresa\stramlitAPP\lotes\online\main.py
# pipreqs --encoding utf-8 "D:\Dropbox\Empresa\stramlitAPP\lotes\online"

st.set_page_config(layout="wide",initial_sidebar_state="expanded")

user     = st.secrets["user"]
password = st.secrets["password"]
host     = st.secrets["host"]
schema   = st.secrets["schema"]
engine   = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')

@st.experimental_memo
def getpolygon():
    data   = pd.read_sql_query("""SELECT scacodigo,scanombre,ST_AsText(geometry) as geometry FROM lotes.dom_geometry_barrios_piloto1"""  , engine)
    geojson = {
    'type': 'FeatureCollection',
    'features': []
    }
    
    for _, row in data.iterrows():
        # Crea una feature (característica) para cada fila del DataFrame
        feature = {
            'type': 'Feature',
            'properties': {},
            'geometry': mapping(wkt.loads(row['geometry']))
        }
        # Agrega las propiedades de la característica
        for prop in ['scacodigo', 'scanombre']:
            feature['properties'][prop] = row[prop]
        # Agrega la característica a la lista de características
        geojson['features'].append(feature)
        
    return geojson

data = getpolygon()


m   = folium.Map(location=[4.693925, -74.054575], zoom_start=15,tiles="cartodbpositron")
folium.GeoJson(data).add_to(m)
st_map = st_folium(m,width=800,height=450)
