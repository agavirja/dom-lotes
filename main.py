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
# streamlit run D:\Dropbox\Empresa\stramlitAPP\lotes\main.py
# pipreqs --encoding utf-8 "D:\Dropbox\Empresa\stramlitAPP\lotes\online"

st.set_page_config(layout="wide",initial_sidebar_state="expanded")

def getinput(x,pos,typeinput):
    try:
        return str(x[pos][typeinput])
    except: return None
   
def getinputjson(x,typeinput):
    try:
        return x[typeinput]
    except: return None
    

def getdatalotes():
    datalotes       = pd.read_pickle('data/app_datalotes')
    datalotes       = datalotes.sort_values(by='indicador',ascending=False)
    datalotes['id'] = range(len(datalotes))
    return datalotes



datalotes = getdatalotes()
st.dataframe(datalotes)
        