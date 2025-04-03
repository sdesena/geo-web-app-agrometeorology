#%%
# Monitoramento Agrometeorológico com Google Earth Engine e Streamlit
import streamlit as st
import geemap.foliumap as geemap
import ee
import plotly.express as px
import pandas as pd
import geopandas as gpd
import json
import os
from datetime import datetime
import altair as alt
import geemap

#%%
# Importar funções auxiliares do código functions.py 





#%%
# Configuração da página
st.set_page_config(layout="wide")

# Definindo o ícone da página
st.title("Monitoramento Agrometeorológico 🌍")
st.sidebar.image('utils/logo_geodata_lab.png')

# Adicionando o autor do código na barra lateral
st.sidebar.markdown('Desenvolvido por [Sandro de Sena](https://www.linkedin.com/in/sandro-sena/)')

# Adicionando a descrição do aplicativo
st.markdown("""
#### 🌿 Aplicativo de Análise Agrometeorológica  

Este aplicativo permite a visualização e análise de dados **agrometeorológicos** diretamente do **Google Earth Engine (GEE)**, facilitando o monitoramento climático e ambiental em diferentes regiões do Brasil.  

### 📌 Funcionalidades:
✅ **Selecionar um município ou estado** para análise.  
✅ **Visualizar mapas interativos** com dados espaciais.  
✅ **Explorar séries temporais** de variáveis climáticas essenciais.  
✅ **Gerar gráficos e mapas** de indicadores como:  
   - **Precipitação e Temperatura Média**  
   - **Balanço Hídrico e Índice SPEI** 

A ferramenta é ideal para acompanhamento de **riscos climáticos**, impactos da variabilidade do clima na agricultura e monitoramento ambiental.  
""")

# Inicializar Google Earth Engine
ee.Initialize()

# Carregar os assets do usuário no GEE
ESTADOS_ASSET = "projects/ee-sandrosenamachado/assets/BR_UF_2023"
MUNICIPIOS_ASSET = "projects/ee-sandrosenamachado/assets/BR_Municipios_2023"

# Função para obter a lista de estados
def get_estados():
    estados = ee.FeatureCollection(ESTADOS_ASSET)
    lista_estados = estados.aggregate_array("NM_UF").getInfo()
    return sorted(lista_estados)

# Função para obter municípios com base no estado selecionado
def get_municipios(estado):
    municipios = ee.FeatureCollection(MUNICIPIOS_ASSET)
    municipios_estado = municipios.filter(ee.Filter.eq("NM_UF", estado))
    lista_municipios = municipios_estado.aggregate_array("NM_MUN").getInfo()
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


# Adicionar campos de datas iniciais e finais na barra lateral
st.sidebar.header("Seleção de Período")
start_date = st.sidebar.date_input("📅 Data inicial", datetime(2023, 1, 1))
end_date = st.sidebar.date_input("📅 Data final", datetime.now())

# Criação e configuração do mapa
m = geemap.Map()

# Ponto central para o mapa (ajuste as coordenadas conforme necessário)
point = ee.Geometry.Point(-45.259679, -17.871838)
m.centerObject(point, 8)
m.setOptions("HYBRID")


