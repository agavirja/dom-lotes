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
    data['geometry'] = data['geometry'].apply(wkt.loads)
    #data['geometry'] = data['geometry'].apply(lambda x: wkt.loads(x))
    data     = gpd.GeoDataFrame(data, geometry='geometry',crs="EPSG:4326")
    #data.crs = "EPSG:4326"
    #data     = data.to_crs("EPSG:4326")
    
    datas = data[['scacodigo']]
    datas['value'] = data['scacodigo'].apply(lambda x: random.uniform(0,100))
    
    return data,datas

data,datas = getpolygon()

#st.write(data)

map0  = folium.Map(location=[4.693925, -74.054575], zoom_start=13,tiles="CartoDB dark_matter")

folium.Choropleth(
    geo_data=data,
    name='Choropleth',
    data=datas,
    columns=['scacodigo','value'],
    key_on='feature.properties.scacodigo',
    fill_color='YlGn',
    fill_opacity=0.15,
    line_opacity=0.1,
    nan_fill_opacity=0.05,
).add_to(map0)

st_map = st_folium(map0,width=1500, height=800)      


