# Monitoramento Agrometeorológico 🌍

Este repositório reúne um conjunto de scripts em Python para análise e visualização de dados agrometeorológicos, integrando o Google Earth Engine (GEE) e Streamlit. O objetivo é apoiar o monitoramento climático, a avaliação agrícola e a gestão ambiental em diferentes regiões do Brasil.

## 📌 Funcionalidades

- Seleção interativa de estados e municípios para análise.
- Visualização de mapas temáticos e interativos.
- Exploração de séries temporais de variáveis climáticas.
- Geração de gráficos e indicadores como:
  - **Precipitação**
  - **Temperatura Média**
  - **Evapotranspiração**
  - **Balanço Hídrico**

## 🛠️ Tecnologias Utilizadas

- Python
- Streamlit
- Google Earth Engine (via API Python)
- Geemap
- Plotly
- Pandas

## 📂 Estrutura do Projeto

- `pages/01_🌧️_Precipitação.py`: Análise de precipitação.
- `pages/02_🌡️_Temperatura.py`: Análise de temperatura média.
- `pages/03_🌳_Evapotranspiração.py`: Análise de evapotranspiração e balanço hídrico.
- `home.py`: Página inicial e apresentação do autor.
- `assets/`: Imagens e logos utilizados na interface.
- `requirements.txt`: Lista de dependências do projeto.

## ℹ️ Observações

- O uso dos scripts requer autenticação no Google Earth Engine e configuração prévia do ambiente Python.
- As análises são realizadas via interface web interativa, permitindo ao usuário selecionar regiões e períodos de interesse.
- Os resultados incluem mapas, gráficos, estatísticas descritivas e tabelas interativas para apoiar a tomada de decisão em contextos ambientais e agrícolas.

---

## ⚠️ Direitos Autorais

Este projeto é protegido por direitos autorais. **Todos os direitos reservados.**
Não é permitida a cópia, reprodução, distribuição ou modificação, total ou parcial, deste código sem autorização prévia e expressa do autor.

Para obter permissão de uso, entre em contato: [Sandro de Sena](https://www.linkedin.com/in/sandro-sena/)