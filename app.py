# importar librerías

import streamlit as st
import numpy as np
import json 
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

st.set_page_config(layout='wide')

df = pd.read_csv('gastos_def_2024.csv')
years = df['year'].unique()
sectors = df['sector_code'].unique()
entities = df['entidad'].unique()

prices = {"corrientes": 'cop',
          "constantes 2018": 'cop_def',
          "constantes 2024": 'cop_def_2024'}



st.title("Histórico del Presupuesto Genreal de la nación (2013-2024)")

tab1, tab2, tab3, tab4 = st.tabs(['Treemap', 'Sectores', 'Entidades', 'Árbol - PGN'])

with tab1:
    year = st.slider("Seleccione el año", 
                     min_value=min(years),
                     max_value=max(years))
    price = st.selectbox("Seleccione el nivel de precios",
                         prices.keys())
    filter_year = df[df['year'] == year]

    fig = px.treemap(filter_year, 
                     path=[px.Constant("PGN"),
                               'sector_code', 
                               'entidad', 
                               'cuenta'],
                    values=prices[price])
    
    st.plotly_chart(fig)

with tab2:
    sector = st.selectbox("Seleccione el sector",
                          sectors)
    
    filter_sector = df[df['sector_code'] == sector]


    pivot_sectors = filter_sector.pivot_table(index='year',
                                           columns='entidad',
                                           aggfunc='sum',
                                           values=prices.values())

    fig, axes = plt.subplots(1, 3, figsize=(14, 6), sharey=True)
    for idx, price in enumerate(pivot_sectors.columns.get_level_values(0)):
        pivot_sectors[price].plot(kind='area', 
                                  ax=axes[idx],
                                  cmap='Blues')
        axes[idx].spines['top'].set_visible(False)
        axes[idx].spines['right'].set_visible(False)
    

    fig.suptitle(f"Histórico por sector: {sector}")
    fig.tight_layout()
    st.pyplot(fig)
    fig.savefig(f"area_plots_sector_{sector}.png")

    with open(f"area_plots_sector_{sector}.png", "rb") as file:

        st.download_button(label="Descargar gráfico",
                           data=file,
                           file_name=f"area_plots_sector_{sector}.png",
                           mime="image/png")

with tab3:
    sector = st.selectbox("Seleccione el sector", sectors, key=2)
    filter_sector = df[df['sector_code'] == sector]
    entities_sector = filter_sector['entidad'].unique()
    entidad = st.selectbox("Seleccione la entidad",
                            entities_sector)
    
    filter_entity = filter_sector[filter_sector['entidad'] == entidad]

    pivot_entity = filter_entity.pivot_table(index='year',
                                           values=prices.values(),
                                           aggfunc='sum')
    if st.button("Graficar histórico"):
        fig, axes = plt.subplots(1, 3, figsize=(14, 6), sharey=True)
        for idx, col in enumerate(pivot_entity):
            pivot_sectors[col].plot(kind='line', 
                                  ax=axes[idx])
            axes[idx].spines['top'].set_visible(False)
            axes[idx].spines['right'].set_visible(False)

        fig.suptitle(f"Histórico por entidad: {entidad}")
        fig.tight_layout()
        st.pyplot(fig)
        fig.savefig(f"line_plots_{entidad}.png")

        with open(f"line_plots_{entidad}.png", "rb") as file:

            st.download_button(label="Descargar gráfico", key=3,
                           data=file,
                           file_name=f"line_plots_{entidad}.png",
                           mime="image/png")

with tab4:

    with open('dictio.json', 'rb') as js:
        dictio = json.load(js)

    json_string = json.dumps(dictio)
    st.json(json_string, expanded=False)

    st.download_button(
        label='Descargar JSON',
        file_name='dictio.json',
        mime="application/json",
        data=json_string
    )


