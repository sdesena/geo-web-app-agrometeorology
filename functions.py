# Instalando bibliotecas necessárias para o funcionamento do código

#%%
# %pip install streamlit
# %pip install streamlit-folium
# %pip install folium
# %pip install geemap
# %pip install earthengine-api
# %pip install plotly
# %pip install pandas
# %pip install geopandas
# %pip install fiona
# %pip install shapely
# %pip install requests
# %pip install matplotlib
# %pip install seaborn

# %% 
# Bash
# python.exe -m pip install --upgrade pip

# %%
# Bash
# pip freeze > requirements.txt

# %%
# Bash
# pip install -r requirements.txt

# %%
# Funções auxiliares para o aplicativo de monitoramento agrometeorológico

import streamlit as st
import ee
import geemap

# Inicializar Google Earth Engine
ee.Initialize()

# Carregar os assets do usuário no GEE
ESTADOS_ASSET = "projects/ee-sandrosenamachado/assets/BR_Estados"
MUNICIPIOS_ASSET = "projects/ee-sandrosenamachado/assets/BR_Municipios"

# Função para obter a lista de estados
def get_estados():
    estados = ee.FeatureCollection(ESTADOS_ASSET)
    lista_estados = estados.aggregate_array("nome").getInfo()
    return sorted(lista_estados)

# Função para obter municípios com base no estado selecionado
def get_municipios(estado):
    municipios = ee.FeatureCollection(MUNICIPIOS_ASSET)
    municipios_estado = municipios.filter(ee.Filter.eq("estado", estado))
    lista_municipios = municipios_estado.aggregate_array("nome").getInfo()
    return sorted(lista_municipios)

# Sidebar para seleção de estado e município
st.sidebar.header("Seleção de Região")
estados = get_estados()
estado_selecionado = st.sidebar.selectbox("Escolha o Estado", estados)

if estado_selecionado:
    municipios = get_municipios(estado_selecionado)
    municipio_selecionado = st.sidebar.selectbox("Escolha o Município", municipios)
    
    st.write(f"### Estado Selecionado: {estado_selecionado}")
    st.write(f"### Município Selecionado: {municipio_selecionado}")