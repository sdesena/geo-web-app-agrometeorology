import geemap               # Ferramentas para integração com o Google Earth Engine e mapas interativos
import ee                   # Biblioteca oficial do Google Earth Engine para Python (processamento de dados geoespaciais)
import geemap.foliumap as geemap  # Versão do geemap baseada no folium, usada para renderizar mapas no Streamlit
from datetime import datetime       # Utilizado para manipular datas (seleção do período de análise)
import streamlit as st              # Framework principal do app (interface web interativa)
import pandas as pd          # Manipulação de tabelas e dataframes            
import plotly.graph_objects as go  # Usado para gráficos avançados (ex: série temporal, indicadores)
import plotly.express as px  # Gráficos simples e rápidos)
import json                 # Manipulação de arquivos JSON (ex: credenciais do GEE)


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
### Análise de Balanço Hídrico (Precipitação - Evapotranspiração)

Esta página permite analisar a dinâmica da evapotranspiração e do balanço hídrico em diferentes municípios do Brasil, utilizando dados do Google Earth Engine.  
A evapotranspiração representa a soma da água evaporada do solo e transpirada pelas plantas, sendo fundamental para entender a disponibilidade hídrica, o manejo agrícola e o monitoramento de secas.  
O balanço hídrico (precipitação menos evapotranspiração) indica períodos de déficit ou excesso de água, auxiliando na gestão de recursos hídricos e planejamento agrícola.

**Fonte dos dados:**  
- Precipitação: CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data)  
- Evapotranspiração: MODIS MOD16A2GF (NASA)

**Análises disponíveis:**  
- Séries temporais anuais e mensais de evapotranspiração e balanço hídrico  
- Gráficos de tendência e sazonalidade  
- Estatísticas descritivas e tabela interativa dos resultados

---
""")


# Inicializar Google Earth Engine
# Autenticação do Google Earth Engine para deploy (conta de serviço)
if "GEE_CREDENTIALS_JSON" in st.secrets:
    # Caso você tenha colocado o JSON inteiro no secrets
    service_account_info = json.loads(st.secrets["GEE_CREDENTIALS_JSON"])
    credentials = ee.ServiceAccountCredentials(service_account_info["client_email"], key_data=service_account_info)
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


# ====================================================
# Visuazalização da Região de Interesse (ROI) no mapa
# ====================================================

    with st.spinner("Renderizando mapa da região de interesse..."):

        # Cria o mapa GEEMAP com a ROI
        m = geemap.Map(height=600)
        m.centerObject(roi, 8)
        m.setOptions("HYBRID")
        m.addLayer(roi, {}, "Região de Interesse")

        # Renderiza o mapa no Streamlit
        m.to_streamlit()


# Só executa as análises após clicar no botão
if run_analysis and roi is not None:

    # Extraindo os anos do período selecionado
    start_year = start_date.year
    end_year = end_date.year
    years = list(range(start_year, end_year + 1))
    months = list(range(1, 13))


    with st.spinner("Carregando dados de precipitação e evapotranspiração..."):
    ## Abrindo nossos dados
        chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/PENTAD").select('precipitation')

        # Definindo a função de escala
        def scale_mod16(image):
            return image.multiply(0.1).copyProperties(image, image.propertyNames())

        mod16 = ee.ImageCollection("MODIS/061/MOD16A2GF").map(scale_mod16 ).select('ET')

    
    # Filtrando a coleção de precipitação e evapotranspiração para o período selecionado
    with st.spinner("Processando séries temporais mensais..."):
        # Definição de período
        year_start = start_date.year
        year_end = end_date.year

        # Parâmetros para padronização temporal
        startDate = ee.Date.fromYMD(year_start, 1, 1)
        endDate = ee.Date.fromYMD(year_end, 1, 1)  # Avança o ano inicial mais x

        # Filtrar a coleção a partir do período definido
        yearFiltered = chirps.filter(ee.Filter.date(startDate, endDate)).filterBounds(roi)
        # print('Numero de imagens',yearFiltered.size().getInfo())

        # Lista de meses e anos
        months = ee.List.sequence(1, 12)
        years = ee.List.sequence(year_start, (year_end - 1))

        # Função para criar imagens mensais
        def createYearly(year):

            def createMonthlyImage(month):
                return yearFiltered \
                    .filter(ee.Filter.calendarRange(year, year, 'year')) \
                    .filter(ee.Filter.calendarRange(month, month, 'month')) \
                    .sum() \
                    .clip(roi) \
                    .set('year', year) \
                    .set('month', month) \
                    .set('data', ee.Date.fromYMD(year, month, 1).format()) \
                    .set('system:time_start', ee.Date.fromYMD(year, month, 1))

            return months.map(createMonthlyImage)

        # Aplicar função mês/ano nas coleções
        chirps_monthlyImages = ee.ImageCollection.fromImages(years.map(createYearly).flatten())
        yearFiltered = mod16.filter(ee.Filter.date(startDate, endDate)).filterBounds(roi)
        mod16_monthlyImages = ee.ImageCollection.fromImages(years.map(createYearly).flatten())

        # Verificar número de bandas
        def addNumBands(image):
            num_bands = image.bandNames().size()
            return image.set('nbands', num_bands)

        # Aplica a função e filtra imagens com bandas válidas
        mod16_monthlyImages = mod16_monthlyImages.map(addNumBands).filter(ee.Filter.gt('nbands', 0))
        chirps_monthlyImages = chirps_monthlyImages.map(addNumBands).filter(ee.Filter.gt('nbands', 0))

        ## Cálculo do Balanço Hídrico
        def calculateWaterBalance(image):
            P = image.select('precipitation')
            ET = image.select('ET')
            waterBalance = P.subtract(ET)
            return image.addBands([waterBalance.rename('water_balance')])

        # Adicionar bandas de precipitação e evapotranspiração às imagens CHIRPS
        def addETBands(image):
            ET_image = mod16_monthlyImages \
                .filter(ee.Filter.eq('year', image.get('year'))) \
                .filter(ee.Filter.eq('month', image.get('month'))) \
                .first()
            return image.addBands([ET_image.rename('ET')])

        # Aplica as funções
        waterBalanceWithBands = chirps_monthlyImages.map(addETBands)
        waterBalanceResult = waterBalanceWithBands.map(calculateWaterBalance)

        ## Função para extrair estatísticas das imagens
        def stats(image):
            reduce = image.reduceRegions(**{
                'collection': roi,
                'reducer': ee.Reducer.mean(),
                'scale': 5000
            })

            reduce = reduce \
                .map(lambda f: f.set({'data': image.get('data')})) \
                .map(lambda f: f.set({'year': image.get('year')})) \
                .map(lambda f: f.set({'month': image.get('month')}))

            return reduce.copyProperties(image, image.propertyNames())

        # Converter para df
        col_bands = waterBalanceResult  # .select(bands)

        # Aplicar estatísticas
        stats_reduce = col_bands.map(stats) \
            .flatten() \
            .sort('data', True)
    

        df = geemap.ee_to_df(stats_reduce)
    

    # ===================== ANÁLISE DE EVAPOTRANSPIRAÇÃO E BALANÇO HÍDRICO =====================
with st.spinner("Gerando gráficos e análises..."):
    st.subheader("Análise Gráfica da Evapotranspiração e Balanço Hídrico")


    # Organizar datas
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')
    df['ano'] = df['data'].dt.year
    df['mes'] = df['data'].dt.month


# ----------- ANÁLISE ANUAL -----------
    annual_data = df.groupby('ano').agg({
        'ET': 'mean',
        'water_balance': 'mean'
    }).reset_index()

    fig_annual = go.Figure()
    fig_annual.add_trace(go.Bar(
        x=annual_data['ano'], y=annual_data['ET'],
        name='Evapotranspiração Média Anual', marker_color='#ff8800'
    ))
    fig_annual.add_trace(go.Bar(
        x=annual_data['ano'], y=annual_data['water_balance'],
        name='Balanço Hídrico Médio Anual', marker_color='#00bfff'
    ))
    fig_annual.update_layout(
        barmode='group',
        title='Evapotranspiração e Balanço Hídrico Médios Anuais',
        xaxis_title='Ano', yaxis_title='Valor (mm/mês)'
    )
    st.plotly_chart(fig_annual, use_container_width=True)

    # ----------- ANÁLISE MENSAL (SAZONALIDADE) -----------
    monthly_data = df.groupby('mes').agg({
        'ET': 'mean',
        'water_balance': 'mean'
    }).reset_index()

    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(
        x=monthly_data['mes'], y=monthly_data['ET'],
        name='Evapotranspiração Média Mensal', marker_color='#ff8800'
    ))
    fig_monthly.add_trace(go.Bar(
        x=monthly_data['mes'], y=monthly_data['water_balance'],
        name='Balanço Hídrico Médio Mensal', marker_color='#00bfff'
    ))
    fig_monthly.update_layout(
        barmode='group',
        title='Evapotranspiração e Balanço Hídrico Médios Mensais',
        xaxis_title='Mês', yaxis_title='Valor (mm/mês)'
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    # ----------- SÉRIE TEMPORAL COM MÉDIA MÓVEL -----------
    df['ET_rolling'] = df['ET'].rolling(window=3, center=True).mean()
    df['wb_rolling'] = df['water_balance'].rolling(window=3, center=True).mean()

    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=df['data'], y=df['ET'],
        mode='lines', name='ET', line=dict(color='#ff8800', width=2)
    ))
    fig_ts.add_trace(go.Scatter(
        x=df['data'], y=df['ET_rolling'],
        mode='lines', name='ET (Média Móvel 3 meses)', line=dict(color='#ffbb33', width=3, dash='dash')
    ))
    fig_ts.add_trace(go.Scatter(
        x=df['data'], y=df['water_balance'],
        mode='lines', name='Balanço Hídrico', line=dict(color='#00bfff', width=2)
    ))
    fig_ts.add_trace(go.Scatter(
        x=df['data'], y=df['wb_rolling'],
        mode='lines', name='Balanço Hídrico (Média Móvel 3 meses)', line=dict(color='#005577', width=3, dash='dash')
    ))
    fig_ts.update_layout(
        title='Série Temporal de Evapotranspiração e Balanço Hídrico',
        xaxis_title='Data', yaxis_title='Valor (mm/mês)'
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    # ----------- ESTATÍSTICAS DESCRITIVAS -----------
    st.subheader("Estatísticas Descritivas")
    st.write("**Evapotranspiração (ET):**")
    st.dataframe(df['ET'].describe().to_frame().T, use_container_width=True)
    st.write("**Balanço Hídrico (P-ET):**")
    st.dataframe(df['water_balance'].describe().to_frame().T, use_container_width=True)

    # ----------- TABELA INTERATIVA -----------
    st.subheader("Tabela de Dados Mensais")
    st.dataframe(df[['data', 'ET', 'water_balance']], use_container_width=True)
