#%%
# Monitoramento Agrometeorológico com Google Earth Engine e Streamlit

import geemap               # Ferramentas para integração com o Google Earth Engine e mapas interativos
import ee                   # Biblioteca oficial do Google Earth Engine para Python (processamento de dados geoespaciais)
import geemap.foliumap as geemap  # Versão do geemap baseada no folium, usada para renderizar mapas no Streamlit
from datetime import datetime       # Utilizado para manipular datas (seleção do período de análise)
import streamlit as st              # Framework principal do app (interface web interativa)
import plotly.express as px  # Gráficos simples e rápidos)
import pandas as pd          # Manipulação de tabelas e dataframes                 # Pausa no processamento (ex: spinner de carregamento)


#%%
# Configuração da página
st.set_page_config(layout="wide")

# Definindo o ícone da página
st.title("Monitoramento Climático e Agrícola 🌍")
st.sidebar.image('assets/logo_geodata_lab_2.png')

# Adicionando o autor do código na barra lateral
st.sidebar.markdown('Desenvolvido por [Sandro de Sena](https://www.linkedin.com/in/sandro-sena/)')

# Adicionando a descrição da página
st.markdown("""
### Análise de Precipitação (mm)

Esta página permite analisar a dinâmica da precipitação em diferentes municípios do Brasil, utilizando dados do Google Earth Engine.

A precipitação é um dos principais componentes do ciclo hidrológico e fundamental para o monitoramento climático, planejamento agrícola, gestão de recursos hídricos e avaliação de riscos de eventos extremos como secas e enchentes. 
            
A análise detalhada da precipitação auxilia na compreensão de padrões sazonais, tendências de chuva e na tomada de decisão para agricultura, abastecimento e meio ambiente.

**Fonte dos dados:**  
- Precipitação: CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data) — série temporal diária, resolução espacial de 5 km.

**Análises disponíveis:**  
- Séries temporais anuais e mensais da precipitação  
- Gráficos de tendência, sazonalidade e média móvel  
- Estatísticas descritivas e tabela interativa dos resultados

---
""")


# Inicializar Google Earth Engine
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
@st.cache_data
def get_estados():
    estados = ee.FeatureCollection(ESTADOS_ASSET)
    lista_estados = estados.aggregate_array("NM_UF").getInfo()
    return sorted(lista_estados)

# Função para obter municípios com base no estado selecionado
@st.cache_data
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
st.sidebar.markdown("Defina o intervalo de datas para a análise.")

start_date = st.sidebar.date_input("📅 Data inicial", datetime(2010, 1, 1))
end_date   = st.sidebar.date_input("📅 Data final", datetime(2020, 12, 31))
run_analysis = st.sidebar.button("Executar Análise")

# Verifica se a data inicial é anterior à data final
if start_date >= end_date:
    st.error("A data inicial deve ser anterior à data final.")
    st.stop()

# Verifica se o município foi selecionado
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

    # Carregar o conjunto de dados CHIRPS (precipitação diária)
    with st.spinner("Carregando dados de precipitação..."):
        chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .select("precipitation") \
            .filterDate(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")) \
            .filterBounds(roi)

    # Cálculo da precipitação anual
    with st.spinner("Calculando precipitação anual..."):
        def calc_annual_precip(year):
            year = ee.Number(year)
            start = ee.Date.fromYMD(year, 1, 1)
            end = ee.Date.fromYMD(year, 12, 31)
            precip_sum = chirps.filterDate(start, end).sum().clip(roi)
            return precip_sum.set('year', year).set('system:time_start', start.millis())
        annual_precip_ic = ee.ImageCollection(ee.List(years).map(calc_annual_precip))

    # Ajuste automático do histograma para o mapa
    def get_viz_params(image):
        stats = image.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=roi,
            scale=1000,
            maxPixels=1e9
        )
        min_val = stats.get("precipitation_min").getInfo()
        max_val = stats.get("precipitation_max").getInfo()
        return {"min": min_val, "max": max_val, "palette": ['#ffffff', '#ff3333', '#fff581', '#33ecff', '#6f5eff', '#171cb1']}

    # Mapa com precipitação anual
    st.header("Mapa de Precipitação Anual")
    year_for_map = st.selectbox("Selecione o ano para o mapa", years)
    annual_img = ee.Image(annual_precip_ic.filter(ee.Filter.eq('year', year_for_map)).first())
    viz_params = get_viz_params(annual_img)
    with st.spinner("Renderizando mapa de precipitação anual..."):
        m = geemap.Map()
        m.centerObject(roi, 8)
        m.addLayer(annual_img, viz_params, f"Precipitação Anual {year_for_map}")
        st.write("### Visualização no Mapa")
        m.to_streamlit(height=500)

    # Geração dos gráficos com Plotly
    st.header("Análise Gráfica da Precipitação")

    def get_region_mean(image, band, scale=10000):
        stat = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=scale,
            maxPixels=1e9
        )
        return stat.get(band)

    # Gráfico anual
    with st.spinner("Gerando gráfico anual..."):
        annual_data = []
        for y in years:
            img = ee.Image(annual_precip_ic.filter(ee.Filter.eq('year', y)).first())
            mean_val = get_region_mean(img, "precipitation")
            mean_val = ee.Number(mean_val).getInfo() if mean_val else None
            annual_data.append({"year": y, "precip": mean_val})
        df_annual = pd.DataFrame(annual_data)
        fig_annual = px.bar(df_annual, x="year", y="precip",
                            labels={"year": "Ano", "precip": "Precipitação (mm)"},
                            title="Precipitação Acumulada Anual")
        st.plotly_chart(fig_annual, use_container_width=True)

    # Gráfico mensal
    with st.spinner("Gerando gráfico mensal..."):
        monthly_data = []
        for y in years:
            for m in months:
                start = ee.Date.fromYMD(y, m, 1)
                end = start.advance(1, 'month')
                img = chirps.filterDate(start, end).sum().clip(roi)
                mean_val = get_region_mean(img, "precipitation")
                mean_val = ee.Number(mean_val).getInfo() if mean_val else None
                monthly_data.append({"year": y, "month": m, "precip": mean_val})
        df_monthly = pd.DataFrame(monthly_data)
        df_monthly_avg = df_monthly.groupby("month").mean().reset_index()
        fig_monthly = px.bar(df_monthly_avg, x="month", y="precip",
                             labels={"month": "Mês", "precip": "Precipitação Média (mm)"},
                             title="Precipitação Média Mensal")
        st.plotly_chart(fig_monthly, use_container_width=True)

    # Série temporal mensal com média móvel
    with st.spinner("Gerando série temporal mensal..."):
        df_monthly['date'] = pd.to_datetime(df_monthly['year'].astype(str) + '-' + df_monthly['month'].astype(str) + '-15')
        df_monthly = df_monthly.sort_values('date')
        df_monthly['precip_rolling'] = df_monthly['precip'].rolling(window=3, center=True).mean()
        fig_ts = px.line(df_monthly, x='date', y='precip',
                         labels={'date': 'Data', 'precip': 'Precipitação (mm)'},
                         title='Série Temporal Mensal da Precipitação')
        fig_ts.add_scatter(x=df_monthly['date'], y=df_monthly['precip_rolling'],
                           mode='lines', name='Média Móvel (3 meses)', line=dict(color='black', width=3, dash='dash'))
        st.plotly_chart(fig_ts, use_container_width=True)

    # Estatísticas descritivas
    with st.spinner("Calculando estatísticas descritivas..."):
        st.subheader("###Estatísticas Descritivas da Precipitação Anual")
        st.dataframe(df_annual.describe().transpose(), use_container_width=True)
        max_row = df_annual.loc[df_annual['precip'].idxmax()]
        min_row = df_annual.loc[df_annual['precip'].idxmin()]
        st.markdown(f"**Ano mais chuvoso:** {int(max_row['year'])} ({max_row['precip']:.1f} mm)")
        st.markdown(f"**Ano mais seco:** {int(min_row['year'])} ({min_row['precip']:.1f} mm)")
        fig_box = px.box(df_annual, y="precip", points="all", title="Distribuição da Precipitação Anual")
        st.plotly_chart(fig_box, use_container_width=True)