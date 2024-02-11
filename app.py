import streamlit as st
import numpy as np
import json 
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from io import BytesIO


from utils import DIC_COLORES, convert_df, get_dic_colors, get_dic_colors_area

st.set_page_config(layout='wide')

df = pd.read_csv('gastos_def_2024.csv')
years = list(df['year'].unique())
years = [int(year) for year in years]
sectors = list(df['sector'].unique())
entities = list(df['entidad'].unique())

show = False

prices = {"corrientes": 'apropiacion_corrientes',
          "constantes 2024": 'apropiacion_cons_2024'}

st.title("Histórico del Presupuesto General de la nación (2013-2024)")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Treemap - Sunburst', 
                                              'Sectores', 
                                              'Entidades', 
                                              'Variación real - Entidades', 
                                              'Árbol - PGN', 
                                              'Descargar datos', 'Test Datos desagregados - 2024'])

with tab1:
    year = st.slider("Seleccione el año", 
                     min_value=min(years),
                     max_value=max(years))
    price = st.selectbox("Seleccione el nivel de precios",
                         prices.keys())
    filter_year = df[df['year'] == year]

    dic_treemap = get_dic_colors(filter_year)
    fig = px.treemap(filter_year, 
                     path=[     'sector', 
                               'entidad', 
                               'tipo_gasto'],
                    values=prices[price],
                    color='sector',
                    color_discrete_map=dic_treemap)
    
    fig.update_layout(width=1000, height=600)
    
    st.plotly_chart(fig)
    

    fig = px.sunburst(filter_year, 
                      path=['sector', 'entidad', 'tipo_gasto'], 
                      values=prices[price],
                      color='sector',
                      color_discrete_map=dic_treemap)
    fig.update_layout(width=1000, height=1000)
    st.plotly_chart(fig)




with tab2:

    piv = (df
           .groupby([ 'sector', 'entidad', 'year'])['apropiacion_cons_2024']
           .sum()
           .reset_index()
           .sort_values(by=['year', 'apropiacion_cons_2024'], ascending=False))
    dic_area = get_dic_colors_area(df)

    fig = px.area(piv,
                  x="year",
                  y="apropiacion_cons_2024",
                  color="sector",
                  line_group='entidad',
                  color_discrete_map=dic_area)
    
    fig.update_layout(width=1300, height=750)
    st.plotly_chart(fig)

with tab3:
    sector = st.selectbox("Seleccione el sector", sectors, key=2)
    filter_sector = df[df['sector'] == sector]
    entities_sector = filter_sector['entidad'].unique()
    entidad = st.selectbox("Seleccione la entidad",
                            entities_sector)
    
    filter_entity = filter_sector[filter_sector['entidad'] == entidad]

    pivot_entity = filter_entity.pivot_table(index='year',
                                           values=prices.values(),
                                           aggfunc='sum')
    
    st.dataframe(pivot_entity)
    if st.button("Graficar histórico"):
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
        for idx, col in enumerate(pivot_entity):
            pivot_entity[col].plot(kind='line', 
                                  ax=axes[idx], 
                                  label=entidad,
                                  color='#2c3a9f',
                                  marker='.',
                                  xticks=pivot_entity.index,
                                  ylim = (0, 
                                          pivot_entity[col].max() + pivot_entity[col].max() / 10))
            axes[idx].spines['top'].set_visible(False)
            axes[idx].spines['right'].set_visible(False)
            if idx  == 1:
                axes[idx].legend()
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


    sector = st.selectbox("Seleccione un sector: ", sectors)
    filter_sector = df[df['sector'] == sector] 
    entity = st.selectbox("Seleccione una entidad: ", filter_sector['entidad'].unique())

    filter_s_e = filter_sector[filter_sector['entidad'] == entity]

    piv = filter_s_e.pivot_table(index='year',
                           values='apropiacion_cons_2024',
                           aggfunc='sum'
                           )
    piv['pct'] = piv['apropiacion_cons_2024'].pct_change()
    piv['pct_avg'] = piv['pct'].mean()
    piv['CAGR'] = ((piv.loc[2024, 'apropiacion_cons_2024'] / piv.loc[2013, 'apropiacion_cons_2024']) ** (1/11)) - 1
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    
    axes[0].bar(piv.index, piv['apropiacion_cons_2024'], color='#2c3a9f', label='Presupuesto')
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)
    axes[0].grid(axis='y', color="#f9f9f9",)
    axes[0].legend()

    axes[1].plot(piv.index, piv['pct_avg'], color='green', label='Variación real promedio')
    axes[1].plot(piv.index, piv['pct'], color='gold', label='Variación real')
    axes[1].plot(piv.index, piv['CAGR'], color='darkblue', label='CAGR')
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)
    axes[1].grid(axis='y')
    axes[1].legend()
    

    fig.suptitle("Presupuesto real vs. Variación real")
    st.pyplot(fig)





with tab5:

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

with tab6:
    st.subheader("Descarga de dataset completo")


    binary_output = BytesIO()
    df.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar datos completos',
                    data = binary_output.getvalue(),
                    file_name = 'datos.xlsx')
    
    st.divider()

    # agregar la categoría todos al multiselect 
    #

    st.subheader("Descargar dataset filtrado")
    col1, col2 = st.columns(2)
    with col1:
        sectors_2 = ['Todos'] + sectors
        sectors_selected = st.multiselect("Sector(es)", sectors_2)
        if "Todos" in sectors_selected:
            filter_ss = df[df['sector'].isin(sectors)]
        else:
            filter_ss = df[df['sector'].isin(sectors_selected)]


        entities_2 = ['Todas'] + list(filter_ss['entidad'].unique())

        entities_selected = st.multiselect("Entidad(es)", entities_2)

        if "Todas" in entities_selected:
            entities_selected = list(filter_ss['entidad'].unique())
        #rango de años
        years_2 = ['Todos'] + years
        years_selected = st.multiselect("Año(s)", years_2)

        if "Todos" in years_selected:
            years_selected = years.copy()

        filter_s_e_y = filter_ss[(filter_ss['entidad'].isin(entities_selected)) & (filter_ss['year'].isin(years_selected))]

    with col2:

        price_selected = st.selectbox("Nivel(es) de precios", prices.keys())
        total_or_account = st.selectbox("Suma o por cuenta", ["suma", "por cuenta"])
        if total_or_account == 'suma':
            pivot = (filter_s_e_y.groupby(['year', 
                                          'sector',
                                          'entidad'])[prices[price_selected]]
                                          .sum()
                                          .reset_index())
        
        else:
            pivot = (filter_s_e_y.groupby(['year', 
                                          'sector',
                                          'entidad','tipo_gasto'])[prices[price_selected]]
                                          .sum()
                                          .reset_index())
        if st.button('Vista previa'):
            show = True            
            
    if show:
        st.dataframe(pivot)
        csv = convert_df(pivot)

        st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name='datos.csv',
                mime='text/csv')
        
        binary_output = BytesIO()
        pivot.to_excel(binary_output, index=False)
        st.download_button(label = 'Descargar excel',
                    data = binary_output.getvalue(),
                    file_name = 'datos.xlsx')

with tab7:
    tdd = pd.read_csv('test_desagregados_datos.csv')
    tdd[['cuenta', 'subcuenta', 'proyecto', 'subproyecto']] = tdd[['cuenta', 'subcuenta', 'proyecto', 'subproyecto']].fillna('') 
    fig = px.sunburst(tdd, path=[px.Constant('PGN'), 
                                 'sector', 
                                 'entidad', 
                                 'cuenta_g', 'cuenta', 'subcuenta'], 
                                  values='total',
                      color='sector_code')
    st.plotly_chart(fig)

    csv = convert_df(tdd)

    st.download_button(
                label="Descargar datos desagregados - 2024",
                data=csv,
                file_name='datos_desagregados_2024.csv',
                mime='text/csv')

