# Monitoramento Agrometeorológico 🌍

Este repositório contém um aplicativo desenvolvido em Python para análise e monitoramento agrometeorológico utilizando o **Google Earth Engine (GEE)** e **Streamlit**.

## 📌 Funcionalidades
- ✅ Seleção de estados e municípios para análise.
- ✅ Visualização de mapas interativos com dados espaciais.
- ✅ Exploração de séries temporais de variáveis climáticas.
- ✅ Geração de gráficos e mapas de indicadores como:
  - **Precipitação e Temperatura Média**
  - **Balanço Hídrico e Índice SPEI**

## 🛠️ Tecnologias Utilizadas
- **Python**
- **Streamlit**
- **Google Earth Engine**
- **Geemap**

## 📂 Estrutura do Projeto
- `geo_web_app.py`: Código principal do aplicativo.
- `functions.py`: Funções auxiliares para processamento de dados.
- `requirements.txt`: Dependências do projeto.
- `utils/`: Recursos adicionais, como imagens e logos.

## 🚀 Como Executar
1. Clone este repositório:
   ```bash
   git clone https://github.com/<seu-usuario>/web-gis-applications.git

2. Instale as dependências:
pip install -r requirements.txt

3. Execute o aplicativo:
streamlit run geo_web_app.py