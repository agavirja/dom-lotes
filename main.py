import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd
from shapely.geometry import Point
from bs4 import BeautifulSoup

from html_scripts import table2,boxkpi

from shapely import wkt
from sqlalchemy import create_engine 
from shapely.geometry import mapping

# streamlit run D:\Dropbox\Empresa\stramlitAPP\lotes\online\main.py
# pipreqs --encoding utf-8 "D:\Dropbox\Empresa\stramlitAPP\lotes\online"

st.set_page_config(layout="wide",initial_sidebar_state="expanded")

user     = st.secrets["user"]
password = st.secrets["password"]
host     = st.secrets["host"]
schema   = st.secrets["schema"]
engine   = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')

def getinput(x,pos,typeinput):
    try:
        return str(x[pos][typeinput])
    except: return None
   
def getinputjson(x,typeinput):
    try:
        return x[typeinput]
    except: return None
    
def data2geojson(data,variables):
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
        for prop in variables:
            feature['properties'][prop] = row[prop]
        # Agrega la característica a la lista de características
        geojson['features'].append(feature)
        
    return geojson

@st.experimental_memo
def getpolygon():
    
    #datalotes       = pd.read_pickle('data/app_datalotes')
    #datalotes       = datalotes.sort_values(by='indicador',ascending=False)
    #datalotes['id'] = range(len(datalotes))

    datalotes       = pd.read_pickle('data/app_datalotes')
    datalotes       = datalotes.sort_values(by='indicador',ascending=False)
    datalotes['id'] = range(len(datalotes))
    
    data         = pd.read_sql_query("""SELECT code,ST_AsText(geometry) as geometry FROM lotes.dom_geometry_lotes_piloto1"""  , engine)
    variables    = ['code']
    datageometry = data2geojson(data,variables)
    
    consulta        = '"'+'","'.join(datalotes['scacodigo'].unique())+'"'
    data            = pd.read_sql_query(f"""SELECT scacodigo,scanombre,ST_AsText(geometry) as geometry FROM lotes.dom_geometry_barrios_piloto1 WHERE scacodigo IN ({consulta})"""  , engine)
    variables       = ['scacodigo', 'scanombre']
    barriocatastral = data2geojson(data,variables)
    
    return datageometry,datalotes,barriocatastral

@st.experimental_memo
def getinfolote(barmanpre):
    datachips        = pd.read_pickle('data/app_datachips')
    datachips        = datachips[datachips['barmanpre']==barmanpre]
    datapropietarios = pd.DataFrame()
    if datachips.empty is False:
        datapropietarios = pd.read_pickle('data/app_datapropietarios')
        datapropietarios = datapropietarios[datapropietarios['chip'].isin(datachips['prechip'])]
    return datachips,datapropietarios

datageometry,datalotes,barriocatastral = getpolygon()

datalotesmap   = datalotes.copy()
datalotestudio = pd.DataFrame()

lng = -74.054575
lat =  4.693925
latpoint = None
lngpoint = None

col1, col2 = st.columns([1,5])


with col1:
    areaterreno  = st.slider('Area de terreno',300, 400, (300, 400))
    datalotesmap = datalotesmap[(datalotesmap['areaterreno']>=areaterreno[0]) & (datalotesmap['areaterreno']<=areaterreno[1])]

    caprate      = st.slider('Cap rate',round(datalotesmap['caprate'].min()*100)/100, round(datalotesmap['caprate'].max()*100)/100, (round(datalotesmap['caprate'].min()*100)/100, round(datalotesmap['caprate'].max()*100)/100))
    datalotesmap = datalotesmap[(datalotesmap['caprate']>=caprate[0]) & (datalotesmap['caprate']<=caprate[1])]

    lotesxbarrio = st.slider('Lotes por barrio',int(datalotesmap['lotesxbarrio'].min()),int(datalotesmap['lotesxbarrio'].max()), (int(datalotesmap['lotesxbarrio'].min()),int(datalotesmap['lotesxbarrio'].max())))
    datalotesmap = datalotesmap[(datalotesmap['lotesxbarrio']>=lotesxbarrio[0]) & (datalotesmap['lotesxbarrio']<=lotesxbarrio[1])]

    tipologiam50mt2 = st.slider('Proporcion de vivienda menor a 50 mt2 en el barrio',round(datalotesmap['50 o menos mt2'].min()*100)/100,round(datalotesmap['50 o menos mt2'].max()*100)/100, (round(datalotesmap['50 o menos mt2'].min()*100)/100,round(datalotesmap['50 o menos mt2'].max()*100)/100))
    datalotesmap    = datalotesmap[(datalotesmap['50 o menos mt2']>=tipologiam50mt2[0]) & (datalotesmap['50 o menos mt2']<=tipologiam50mt2[1])]
    
    #tratamiento  = st.selectbox('Tratamiento urbano',options=['Todos','Consolidacion',''])
    tratamiento = st.selectbox('Tratamiento urbano',options=['Todos']+list(datalotesmap['nombre_trat_urba'].unique()))
    if tratamiento!='Todos':
        datalotesmap = datalotesmap[datalotesmap['nombre_trat_urba']==tratamiento]
    
    area_tratamiento = st.selectbox('Tratamiento urbano',options=['Todos']+list(datalotesmap['nombre_are'].unique()))
    if area_tratamiento!='Todos':
        datalotesmap = datalotesmap[datalotesmap['nombre_are']==area_tratamiento]

    label = 'Total lotes'
    html  = boxkpi(len(datalotesmap),label)
    html_struct = BeautifulSoup(html, 'html.parser')
    st.markdown(html_struct, unsafe_allow_html=True)
    
with col2:
    map0  = folium.Map(location=[lat,lng], zoom_start=13,tiles="CartoDB dark_matter")
    
    folium.GeoJson(datageometry).add_to(map0)
    folium.GeoJson(barriocatastral).add_to(map0)
    
    draw = Draw(
                draw_options={"polygon":False,"polyline": False,"marker": True,"circlemarker":False,"rectangle":False,"circle":False},
                edit_options={"poly": {"allowIntersection": False}}
                )
    draw.add_to(map0)
    
    st_map = st_folium(map0,width=1500, height=800)      
    
    if 'all_drawings' in st_map and st_map['all_drawings'] is not None and st_map['all_drawings']!=[]:
        latpoint = st_map['all_drawings'][0]['geometry']['coordinates'][1]
        lngpoint = st_map['all_drawings'][0]['geometry']['coordinates'][0]
        
df = datalotes[['id','areaterreno']]
#df = datalotes[['id','areaterreno','areaconstruida','predios','vetustex_max','alturamin','alturamax','nombre_trat_urba','valorAutoavaluo']]
#df.columns = ['id','Area Terreno','Area Construida','# de predios','Antiguedad construccion','Altura minima','Altura maxima','Tratamiento','Avaluo Catastral']
st.dataframe(df)
try:
    response = AgGrid(df)
    st.write('aggrid')
except: 
    gb = GridOptionsBuilder.from_dataframe(df)
    st.dataframe(gb)
    st.write('gb')

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
gb.configure_selection(selection_mode="single", use_checkbox=True) # "multiple"
gb.configure_side_bar(filters_panel=False,columns_panel=False)
gridoptions = gb.build()

response = AgGrid(
    df,
    height=350,
    gridOptions=gridoptions,
    enable_enterprise_modules=False,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    header_checkbox_selection_filtered_only=False,
    use_checkbox=True)
        
if response['selected_rows']:
    datalotestudio = datalotes[datalotes['id']==response['selected_rows'][0]['id']]
    
if latpoint is not None and lngpoint is not None:
    st.write(latpoint)
    st.write(lngpoint)
    idd = datageometry['geometry'].apply(lambda x: x.contains(Point(lngpoint,latpoint)))
    if sum(idd)==1:
        datalotestudio = datalotes[datalotes['code']==datageometry[idd]['code'].iloc[0]]
        
if datalotestudio.empty is False:
    barmanpre = datalotestudio['barmanpre'].iloc[0]
    scacodigo = datalotestudio['scacodigo'].iloc[0]   
    
    datachips,datapropietarios = getinfolote(barmanpre)
    
    col1,col2,col3,col4 = st.columns([2,1,1,2])
    
    with col1:
        formato = [{'name':'Dirección','value':'predirecc','data':'datachips'},
                   {'name':'Barrio catastral','value':'prenbarrio','data':'datachips'},
                   {'name':'Area de terreno','value':'areaterreno','data':'datalotestudio'},
                   {'name':'Area construida','value':'areaconstruida','data':'datalotestudio'},
                   {'name':'# Predios en el lote','value':'predios','data':'datalotestudio'},
                   {'name':'Altura maxima','value':'altura_max_trat_urba','data':'datalotestudio'},
                   {'name':'Tratamiento urbano','value':'nombre_trat_urba','data':'datalotestudio'},
                   {'name':'Tipo','value':'nombre_are','data':'datalotestudio'},
                   {'name':'Uso de vivienda','value':'preuviven','data':'datachips'},
                   {'name':'Avaluo catastral','value':'valorAutoavaluo','data':'datapropietarios'},
                   {'name':'Impuesto predial','value':'valorImpuesto','data':'datapropietarios'},
                   {'name':'Estrato','value':'estrato','data':'datalotestudio'},
                   ]
        
        html = ""
        barrio = ""
        for i in formato:
            htmlpaso = ""
            if 'datachips' in i['data']:
                if i['value'] in datachips:
                    htmlpaso += f"""
                    <td>{i["name"]}</td>
                    <td>{datachips[i['value']].iloc[0]}</td>            
                    """
                    if i['value'] in 'prenbarrio':
                        barrio = datachips[i['value']].iloc[0]
                        
            if 'datalotestudio' in i['data']:
                if i['value'] in datalotestudio:
                    htmlpaso += f"""
                    <td>{i["name"]}</td>
                    <td>{datalotestudio[i['value']].iloc[0]}</td>            
                    """
            if 'datapropietarios' in i['data']:
                if i['value'] in datapropietarios:
                    
                    v = datapropietarios[datapropietarios[i['value']].notnull()]
                    w = v.groupby('chip')['vigencia'].max().reset_index()
                    w.columns = ['chip','vigmax']
                    v = v.merge(w,on='chip',how='left',validate='m:1')
                    v = v[v['vigencia']==v['vigmax']]
                    v = v.groupby('chip').agg({i['value']:'sum'}).reset_index()
                    if v.empty is False:
                        valor = f"${v[i['value']].sum():,.0f}"
                        htmlpaso += f"""
                        <td>{i["name"]}</td>
                        <td>{valor}</td>            
                        """
            html += f"""
                <tr>
                {htmlpaso}
                </tr>
            """
                    
        texto = BeautifulSoup(table2(html,'Caracteristicas del lote'), 'html.parser')
        st.markdown(texto, unsafe_allow_html=True)  
                
    with col2:
        if 'caprate' in datalotestudio: 
            capbruto = datalotestudio['caprate'].iloc[0]
            capbruto = "{:.1%}".format(capbruto)
            label    = f'Caprate {barrio}'
            html     = boxkpi(capbruto,label)
            html_struct = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)

    with col3:
        if 'lotesxbarrio' in datalotestudio: 
            valor = datalotestudio['lotesxbarrio'].iloc[0]
            label = f'Lotes de oportunidad en {barrio}'
            html  = boxkpi(valor,label)
            html_struct = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)
            
    with col2:
        if 'valorarriendomt2' in datalotestudio: 
            valor = datalotestudio['valorarriendomt2'].iloc[0]
            valor = f"${valor:,.0f}"
            label = 'Valor arriendo por mt2'
            html  = boxkpi(valor,label)
            html_struct = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)

    with col3:
        if 'valorarriendomt2' in datalotestudio and 'desviacion_arriendo' in datalotestudio: 
            valor = datalotestudio['desviacion_arriendo'].iloc[0]/datalotestudio['valorarriendomt2'].iloc[0]
            valor = "{:.1%}".format(valor)
            label = 'Coef. variacion'
            html  = boxkpi(valor,label)
            html_struct = BeautifulSoup(html, 'html.parser')
            st.markdown(html_struct, unsafe_allow_html=True)
            
            
    with col4:
        datatipologia = []
        for i in ['50 o menos mt2', '50 a 80 mt2', '80 a 100 mt2', '100 a 150 mt2', '150 o más mt2']:
            if i in datalotestudio:
                datatipologia.append({'y':i,'x':datalotestudio[i].iloc[0]})
        datatipologia = pd.DataFrame(datatipologia)
        
        fig = px.bar(datatipologia, x='x', y='y',barmode='group')
        fig.update_traces(textposition='outside')
        fig.update_layout(
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            xaxis_title='',
            yaxis_title='',
            legend_title_text=None,
            #width=800, 
            #height=500
        )        
        st.plotly_chart(fig, theme="streamlit",use_container_width=True)
            
        
    col1, col2 ,col3 = st.columns([4,1,4])
    if datapropietarios.empty is False:
        
        with col1:
            v = datapropietarios.drop_duplicates(subset=['chip','vigencia'],keep='first')
            v = v.groupby('vigencia').agg({'valorAutoavaluo':'sum','valorImpuesto':'sum'}).reset_index()
            # Creando la figura
            fig = go.Figure()
            
            # Agregando la línea para 'valorAutoavaluo'
            fig.add_trace(go.Scatter(
                x=v['vigencia'], 
                y=v['valorAutoavaluo'], 
                name='Avaluo catastral',
                line=dict(color='blue')))
            
            # Creando un eje Y secundario
            fig.update_layout(
                yaxis2=dict(
                    title="Predial",
                    titlefont=dict(color="red"),
                    tickfont=dict(color="red"),
                    overlaying="y",
                    side="right"
                )
            )
            
            # Agregando la línea para 'valorImpuesto'
            fig.add_trace(go.Scatter(
                x=v['vigencia'], 
                y=v['valorImpuesto'], 
                name='Predial',
                line=dict(color='red'),
                yaxis="y2"))
            
            # Definiendo los títulos de los ejes y el título del gráfico
            fig.update_layout(
                xaxis_title="Vigencia",
                yaxis_title="Avaluo catastral",
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            # Mostrando la gráfica en Streamlit
            st.plotly_chart(fig)

        with col3:
            v = datapropietarios.drop_duplicates(subset=['chip','vigencia'],keep='first')
            w = v[['tipoDocumento','numeroIdentificacion', 'naturaleza', 'primerNombre', 'segundoNombre', 'primerApellido', 'email', 'telefonos', 'numeroMatriculaInmobiliaria','numeroChip']]

            w['naturaleza'] = w['naturaleza'].apply(lambda x: getinputjson(x,'nombre'))

            w['telefono1'] = w['telefonos'].apply(lambda x: getinput(x,0,'numero'))
            w['telefono2'] = w['telefonos'].apply(lambda x: getinput(x,1,'numero'))
            w['telefono3'] = w['telefonos'].apply(lambda x: getinput(x,2,'numero'))

            w['email1'] = w['email'].apply(lambda x: getinput(x,0,'direccion'))
            w['email2'] = w['email'].apply(lambda x: getinput(x,1,'direccion'))
            w['email3'] = w['email'].apply(lambda x: getinput(x,2,'direccion'))

            
            w.drop(columns=['telefonos','email'],inplace=True)
            
            w = w[w['tipoDocumento'].notnull()]
            w = w.drop_duplicates(subset='numeroChip',keep='first')
            
            w = w.transpose()
            w.columns = ['propietario ' + str(i+1) for i in range(w.shape[1])]
            w = w.reset_index()
            st.dataframe(w)