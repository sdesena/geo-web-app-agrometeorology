import geemap               # Ferramentas para integração com o Google Earth Engine e mapas interativos
import ee                   # Biblioteca oficial do Google Earth Engine para Python (processamento de dados geoespaciais)
import geemap.foliumap as geemap  # Versão do geemap baseada no folium, usada para renderizar mapas no Streamlit
from datetime import datetime       # Utilizado para manipular datas (seleção do período de análise)
import streamlit as st              # Framework principal do app (interface web interativa)
import plotly.express as px  # Gráficos simples e rápidos)
import pandas as pd          # Manipulação de tabelas e dataframes                 # Pausa no processamento (ex: spinner de carregamento)
import json

#%%
# Configuração da página
st.set_page_config(layout="wide")

# Definindo o ícone da página
st.title("Monitoramento Climático e Agrícola 🌍")
st.sidebar.image('assets/logo_geodata_lab_2.png')

# Adicionando o autor do código na barra lateral
st.sidebar.markdown('Desenvolvido por [Sandro de Sena](https://www.linkedin.com/in/sandro-sena/)')

# Adicionando a descrição dessa página
st.markdown("""
### Análise de Temperatura Média (MODIS)

Esta página permite analisar a dinâmica da temperatura média em diferentes municípios do Brasil, utilizando dados do Google Earth Engine.

A temperatura média é um dos principais indicadores climáticos, fundamental para o monitoramento ambiental, planejamento agrícola, avaliação de riscos de extremos climáticos e estudos de mudanças do clima. A análise detalhada da temperatura auxilia na compreensão de padrões sazonais, tendências de aquecimento ou resfriamento e na tomada de decisão para diversas áreas, como agricultura, saúde e recursos naturais.

**Fonte dos dados:**  
- Temperatura: MODIS MOD11A2 (NASA) — produto de temperatura da superfície terrestre, com resolução espacial de 1 km e composição de 8 dias.

**Análises disponíveis:**  
- Séries temporais anuais e mensais da temperatura média  
- Gráficos de tendência, sazonalidade e média móvel  
- Estatísticas descritivas e tabela interativa dos resultados

---
""")


# Inicializar Google Earth Engine
# Autenticação do Google Earth Engine para deploy (conta de serviço)
if "GEE_CREDENTIALS_JSON" in st.secrets:
    # Caso você tenha colocado o JSON inteiro no secrets
    service_account_info = json.loads(st.secrets["GEE_CREDENTIALS_JSON"])
    credentials = ee.ServiceAccountCredentials(service_account_info["client_id"], key_data=service_account_info)
    ee.Initialize(credentials)
else:
    # Fallback para autenticação local (útil para desenvolvimento local)
    try:
        ee.Initialize()
    except Exception as e:
        ee.Authenticate()
        ee.Initialize()


# Inicializa um mapa apenas para garantir autenticação do Earth Engine
auth_map = geemap.Map()

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
start_date = st.sidebar.date_input("📅 Data inicial", datetime(2010, 1, 1))
end_date   = st.sidebar.date_input("📅 Data final", datetime(2020, 12, 31))
run_analysis = st.sidebar.button("Executar Análise")



# ...código de seleção de estado, município, datas...

if start_date >= end_date:
    st.error("A data inicial deve ser anterior à data final.")
    st.stop()

if not municipio_selecionado:
    st.error("Selecione um município para prosseguir.")
    st.stop()

if run_analysis:
    # Definir a ROI como a geometria do município selecionado
    with st.spinner("Carregando geometria do município..."):
        roi_fc = ee.FeatureCollection(MUNICIPIOS_ASSET) \
                    .filter(ee.Filter.eq("NM_UF", estado_selecionado)) \
                    .filter(ee.Filter.eq("NM_MUN", municipio_selecionado))
        roi = roi_fc.geometry()

    # Visualização da Região de Interesse
    with st.spinner("Renderizando mapa da região de interesse..."):
        m = geemap.Map(height=600)
        m.centerObject(roi, 8)
        m.setOptions("HYBRID")
        m.addLayer(roi, {}, "Região de Interesse")
        m.to_streamlit()

    # Extraindo os anos do período selecionado
    start_year = start_date.year
    end_year = end_date.year
    years = list(range(start_year, end_year + 1))
    months = list(range(1, 13))

    # Carregar o conjunto de dados MODIS MOD11A2 (Temperatura)
    with st.spinner("Carregando dados de temperatura..."):
        modis_temp = ee.ImageCollection("MODIS/006/MOD11A2") \
            .select("LST_Day_1km") \
            .filterDate(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")) \
            .filterBounds(roi)
        modis_temp_celsius = modis_temp.map(lambda img: img.multiply(0.02).subtract(273.15).copyProperties(img, img.propertyNames()))

    # Cálculo da temperatura média anual
    with st.spinner("Calculando temperatura média anual..."):
        def calc_annual_temp(year):
            year = ee.Number(year)
            start = ee.Date.fromYMD(year, 1, 1)
            end = ee.Date.fromYMD(year, 12, 31)
            temp_mean = modis_temp_celsius.filterDate(start, end).mean().clip(roi)
            return temp_mean.set('year', year).set('system:time_start', start.millis())
        annual_temp_ic = ee.ImageCollection(ee.List(years).map(calc_annual_temp))

    # Seleção de ano para visualização no mapa
    year_for_temp_map = st.selectbox("Selecione o ano para o mapa de temperatura", years)
    annual_temp_img = ee.Image(annual_temp_ic.filter(ee.Filter.eq('year', year_for_temp_map)).first())

    # Ajuste automático do histograma para temperatura
    def get_temp_viz_params(image):
        stats = image.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=roi,
            scale=1000,
            maxPixels=1e9
        )
        min_val = stats.get("LST_Day_1km_min").getInfo()
        max_val = stats.get("LST_Day_1km_max").getInfo()
        return {"min": min_val, "max": max_val, "palette": ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']}

    # Renderizar o mapa de temperatura
    with st.spinner("Renderizando mapa de temperatura..."):
        viz_params_temp = get_temp_viz_params(annual_temp_img)
        m_temp = geemap.Map()
        m_temp.centerObject(roi, 8)
        m_temp.addLayer(annual_temp_img, viz_params_temp, f"Temperatura Média Anual {year_for_temp_map}")
        st.write("### Mapa de Temperatura Média Anual")
        m_temp.to_streamlit(height=500)

    # Geração dos gráficos com Plotly
    st.header("Análise Gráfica da Temperatura Média")

    def get_region_mean(image, band, scale=1000):
        stat = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=scale,
            maxPixels=1e9
        )
        return stat.get(band)

    # Gráfico anual
    with st.spinner("Gerando gráfico anual..."):
        annual_temp_data = []
        for y in years:
            img = ee.Image(annual_temp_ic.filter(ee.Filter.eq('year', y)).first())
            mean_val = get_region_mean(img, "LST_Day_1km")
            mean_val = ee.Number(mean_val).getInfo() if mean_val else None
            annual_temp_data.append({"year": y, "temp": mean_val})
        df_annual_temp = pd.DataFrame(annual_temp_data)
        fig_annual_temp = px.line(
            df_annual_temp, x="year", y="temp",
            labels={"year": "Ano", "temp": "Temperatura Média (°C)"},
            title="Temperatura Média Anual",
            line_shape="linear"
        )
        fig_annual_temp.update_traces(line_color="#ff8800", line_width=3, marker_color="#ff8800")
        st.plotly_chart(fig_annual_temp, use_container_width=True)

    # Gráfico mensal
    with st.spinner("Gerando gráfico mensal..."):
        monthly_temp_data = []
        for y in years:
            for m in months:
                start = ee.Date.fromYMD(y, m, 1)
                end = start.advance(1, 'month')
                img = modis_temp_celsius.filterDate(start, end).mean().clip(roi)
                mean_val = get_region_mean(img, "LST_Day_1km")
                mean_val = ee.Number(mean_val).getInfo() if mean_val else None
                monthly_temp_data.append({"year": y, "month": m, "temp": mean_val})
        df_monthly_temp = pd.DataFrame(monthly_temp_data)
        df_monthly_temp_avg = df_monthly_temp.groupby("month").mean().reset_index()
        fig_monthly_temp = px.line(
            df_monthly_temp_avg, x="month", y="temp",
            labels={"month": "Mês", "temp": "Temperatura Média (°C)"},
            title="Temperatura Média Mensal",
            line_shape="linear"
        )
        fig_monthly_temp.update_traces(line_color="#ff8800", line_width=3, marker_color="#ff8800")
        st.plotly_chart(fig_monthly_temp, use_container_width=True)

    # Série temporal mensal com média móvel de 3 meses
    with st.spinner("Gerando série temporal mensal..."):
        df_monthly_temp['date'] = pd.to_datetime(df_monthly_temp['year'].astype(str) + '-' + df_monthly_temp['month'].astype(str) + '-15')
        df_monthly_temp = df_monthly_temp.sort_values('date')
        df_monthly_temp['temp_rolling'] = df_monthly_temp['temp'].rolling(window=3, center=True).mean()
        fig_ts_temp = px.line(
            df_monthly_temp, x='date', y='temp',
            labels={'date': 'Data', 'temp': 'Temperatura Média (°C)'},
            title='Série Temporal Mensal da Temperatura'
        )
        fig_ts_temp.add_scatter(
            x=df_monthly_temp['date'], y=df_monthly_temp['temp_rolling'],
            mode='lines', name='Média Móvel (3 meses)',
            line=dict(color='#ff8800', width=3, dash='dash')
        )
        fig_ts_temp.update_traces(line_color="#ffbb33", selector=dict(mode='lines'))
        st.plotly_chart(fig_ts_temp, use_container_width=True)

    # Estatísticas descritivas da temperatura anual
    with st.spinner("Calculando estatísticas descritivas..."):
        st.subheader("Estatísticas Descritivas da Temperatura Média Anual")
        st.dataframe(df_annual_temp.describe().transpose(), use_container_width=True)
        max_row = df_annual_temp.loc[df_annual_temp['temp'].idxmax()]
        min_row = df_annual_temp.loc[df_annual_temp['temp'].idxmin()]
        st.markdown(f"**Ano mais quente:** {int(max_row['year'])} ({max_row['temp']:.2f} °C)")
        st.markdown(f"**Ano mais frio:** {int(min_row['year'])} ({min_row['temp']:.2f} °C)")
        fig_box_temp = px.box(
            df_annual_temp, y="temp", points="all", title="Distribuição da Temperatura Média Anual",
            color_discrete_sequence=["#ff8800"]
        )
        st.plotly_chart(fig_box_temp, use_container_width=True)