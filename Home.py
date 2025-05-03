import streamlit as st

st.set_page_config(layout="wide")

logo = r"C:\Users\sandr\Documents\GitHub\web-gis-applications\assets\logo_geodata_lab_2.png"

# Adicionando o logo do GeoData Lab na barra lateral
st.sidebar.image(logo)

# Adicionando o autor do código na barra lateral
markdown = """
* [Sandro de Sena](https://www.linkedin.com/in/sandro-sena/)

Pós-graduado em Ciência de Dados, bacharel em Gestão Ambiental e especialista em Geotecnologias aplicadas ao Desenvolvimento Sustentável.

Atuo integrando geoprocessamento, sensoriamento remoto e ciência de dados para apoiar o monitoramento ambiental, o planejamento territorial e a avaliação agrícola e climática.

"""

st.sidebar.title("Sobre o Autor")
st.sidebar.info(markdown)

# Customize page title
st.title("Monitoramento Climático e Agrícola 🌍")

# Adicionando a descrição do aplicativo
st.markdown("""

---

Este aplicativo foi desenvolvido para **visualização e análise de dados agrometeorológicos** diretamente a partir do **Google Earth Engine (GEE)**, oferecendo uma plataforma interativa para o **monitoramento climático e agrícola** em todo o território brasileiro.

Ideal para profissionais e pesquisadores das áreas de **agrometeorologia**, **agricultura de precisão**, **gestão de riscos climáticos** e **planejamento territorial**, o aplicativo fornece **dados atualizados**, **estatísticas detalhadas** e **visualizações interativas**, tudo em poucos cliques.

---

## 🌎 Aplicações

- 🔍 **Monitoramento de Riscos Climáticos Agrícolas**  
- 📉 **Análise de Impactos Climáticos em Safras e Produtividade**  
- 📊 **Suporte à Tomada de Decisão em Políticas Públicas e Gestão Rural**  
- 📍 **Análise Espacial de Estados e Municípios com Dados Remotos**  

---

## 📌 Funcionalidades Principais

- ✅ **Seleção Geográfica Dinâmica**  
  Escolha o **Estado** ou **Município** de interesse para análise localizada.

- 🗺️ **Mapas Interativos**  
  Visualize mapas temáticos com dados espaciais atualizados por região e por período.

- 📈 **Gráficos de Séries Temporais**  
  Explore tendências anuais e mensais por meio de gráficos interativos.

- 📋 **Tabelas e Indicadores**  
  Acesse estatísticas descritivas e exporte tabelas com dados resumidos para análise externa.

---

## 🔎 Fontes de Dados Utilizadas

| Fonte            | Variável              | Resolução Temporal | Resolução Espacial |
|------------------|------------------------|---------------------|---------------------|
| **CHIRPS**       | Precipitação (mm)      | Mensal, Anual       | ~5 km               |
| **MODIS MOD11**  | Temperatura Média (°C) | Mensal, Anual       | ~1 km               |
| **MODIS MOD16**  | Evapotranspiração (mm) | Mensal, Anual       | ~1 km               |

---

## 🧭 Como Usar o Aplicativo

1. **Selecione uma Página**  
   No menu lateral, escolha entre:
   - **Precipitação**
   - **Temperatura**
   - **Evapotranspiração e Balanço Hídrico**

2. **Escolha o Local de Análise**  
   Use os filtros para selecionar o **Estado** ou **Município** desejado.

3. **Visualize os Mapas**  
   Observe a distribuição espacial das variáveis com base no período selecionado.

4. **Explore os Gráficos Temporais**  
   Analise tendências ao longo do tempo.

5. **Consulte e Exporte Tabelas**  
   Veja estatísticas como média, mínimo, máximo e desvio padrão.  

---

Todos os direitos reservados ao autor do aplicativo.

---          

""")

