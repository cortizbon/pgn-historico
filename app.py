import streamlit as st
import numpy as np
import json 
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from io import BytesIO
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

from utils import DIC_COLORES, convert_df, get_dic_colors, get_dic_colors_area

st.set_page_config(layout='wide')

df = pd.read_csv('gastos_def_2024.csv')
years = list(df['Año'].unique())
years = [int(year) for year in years]
sectors = list(df['Sector'].unique())
entities = list(df['Entidad'].unique())
dict_gasto = {'Funcionamiento':DIC_COLORES['az_verd'][2],
              'Deuda':DIC_COLORES['ax_viol'][1],
              'Inversion':DIC_COLORES['ro_am_na'][3]}

show = False


prices = {"corrientes": 'Apropiación a precios corrientes en millones',
          "constantes 2024": 'Apropiación a precios constantes (2024) en millones'}

with st.sidebar:
    selected_option = option_menu("Menú", ["Main", "Histórico general", "Histórico por sector", "Histórico por entidad", "Treemap", "Descarga de datos"], 
        icons=['arrow-right-short', 'file-bar-graph', 'intersect', "list-task", 'columns', 'cloud-download'], 
        menu_icon="p", default_index=0, orientation="vertical")
    
if selected_option == "Main":
    st.header("PePE: Presupuesto en Perpectiva Económica")
elif selected_option == "Histórico general":
    st.header(selected_option)
    piv_2024 = df.groupby('Año')['Apropiación a precios constantes (2024) en millones'].sum().reset_index()
    piv_corr = df.groupby('Año')['apropiacion_corrientes'].sum().reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año',  y_title='Monto en millones de pesos')
    
    fig.add_trace(
        go.Line(
            x=piv_2024['Año'], y=piv_2024['Apropiación a precios constantes (2024) en millones'], 
            name='Apropiación a precios constantes (2024) en millones', line=dict(color=DIC_COLORES['ax_viol'][1])
        ),
        row=1, col=1
    )

    piv_tipo_gasto = (df
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2024) en millones']
                      .sum()
                      .reset_index())
    piv_tipo_gasto['total'] = piv_tipo_gasto.groupby(['Año'])['Apropiación a precios constantes (2024) en millones'].transform('sum')

    piv_tipo_gasto['%'] = ((piv_tipo_gasto['Apropiación a precios constantes (2024) en millones'] / piv_tipo_gasto['total']) * 100).round(2)

        
    for i, group in piv_tipo_gasto.groupby('Tipo de gasto'):
        fig.add_trace(go.Bar(
            x=group['Año'],
            y=group['%'],
            name=i, marker_color=dict_gasto[i]
        ), row=1, col=2)

    fig.update_layout(barmode='stack')
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), title='Histórico general',separators=',')


    st.plotly_chart(fig)



    # distribución de gastos en las principales entidades (2024)
    # sectores con mayor asignación
    # entidades con mayor asignación 

elif selected_option == "Histórico por sector":
    st.header(selected_option)

    sector = st.selectbox("Seleccione el sector", sectors, key=2)
    filter_sector = df[df['Sector'] == sector]

    pivot_sector = filter_sector.pivot_table(index='Año', values=prices.values(), aggfunc='sum').reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año', shared_yaxes=True, y_title='Monto en millones de pesos')
    
    fig.add_trace(
        go.Line(
            x=pivot_sector['Año'], y=pivot_sector['Apropiación a precios constantes (2024) en millones'], 
            name='Apropiación a precios constantes (2024) en millones', line=dict(color=DIC_COLORES['ax_viol'][1])
        ),
        row=1, col=1
    )

    piv_tipo_gasto_sector = (filter_sector
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2024) en millones']
                      .sum()
                      .reset_index())
    for i, group in piv_tipo_gasto_sector.groupby('Tipo de gasto'):
        fig.add_trace(go.Bar(
            x=group['Año'],
            y=group['Apropiación a precios constantes (2024) en millones'],
            name=i, marker_color=dict_gasto[i]
        ), row=1, col=2)

    fig.update_layout(barmode='stack')


    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), title=sector,separators=',')

    st.plotly_chart(fig)

    piv_tipo_gasto = (df
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2024) en millones']
                      .sum()
                      .reset_index())

    st.subheader(f"Variación histórica por sector: {sector}")

    try:
        piv = filter_sector.pivot_table(index='Año',
                            values='Apropiación a precios constantes (2024) en millones',
                            aggfunc='sum'
                            )
        piv['pct'] = piv['Apropiación a precios constantes (2024) en millones'].pct_change()
        piv['pct'] = (piv['pct'] * 100).round(2)
        piv['CAGR'] = ((piv.loc[2024, 'Apropiación a precios constantes (2024) en millones'] / piv.loc[2013, 'Apropiación a precios constantes (2024) en millones']) ** (1/11)) - 1
        piv['CAGR'] = (piv['CAGR'] * 100).round(2)
        piv = piv.reset_index()

        fig = make_subplots(rows=1, cols=2, x_title='Año')

        fig.add_trace(
            go.Bar(x=piv['Año'], y=piv['Apropiación a precios constantes (2024) en millones'],
                name='Apropiación a precios constantes (2024) en millones', marker_color=DIC_COLORES['ofiscal'][1]),
            row=1, col=1, 
        )

        fig.add_trace(go.Line(
                x=piv['Año'], 
                y=piv['pct'], 
                name='Variación porcentual (%)', line=dict(color=DIC_COLORES['ro_am_na'][1])
            ),
            row=1, col=2
        )
        fig.add_trace(
            go.Line(
                x=piv['Año'], y=piv['CAGR'], name='Variación anualizada (%)', line=dict(color=DIC_COLORES['verde'][0])
            ),
            row=1, col=2
        )
        fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1))

        st.plotly_chart(fig)
    except KeyError as e:
        st.error("No hay suficiente información para calcular la variación histórica.")



elif selected_option == "Histórico por entidad":
    st.header(selected_option)
    sector = st.selectbox("Seleccione el sector", sectors, key=2)
    filter_sector = df[df['Sector'] == sector]
    entities_sector = filter_sector['Entidad'].unique()
    entidad = st.selectbox("Seleccione la entidad",
                            entities_sector)
    
    filter_entity = filter_sector[filter_sector['Entidad'] == entidad]

    pivot_entity = filter_entity.pivot_table(index='Año',
                                           values=prices.values(),
                                           aggfunc='sum')
    
    pivot_entity = pivot_entity.reset_index()
    fig = make_subplots(rows=1, cols=2, x_title='Año', shared_yaxes=True, y_title='Monto en millones de pesos')
    
    fig.add_trace(
        go.Line(
            x=pivot_entity['Año'], y=pivot_entity['Apropiación a precios constantes (2024) en millones'], 
            name='Apropiación a precios constantes (2024) en millones', line=dict(color=DIC_COLORES['ax_viol'][1])
        ),
        row=1, col=1
    )
    piv_tipo_gasto_entity = (filter_entity
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2024) en millones']
                      .sum()
                      .reset_index())
    for i, group in piv_tipo_gasto_entity.groupby('Tipo de gasto'):
        fig.add_trace(go.Bar(
            x=group['Año'],
            y=group['Apropiación a precios constantes (2024) en millones'],
            name=i, marker_color=dict_gasto[i]
        ), row=1, col=2)

    fig.update_layout(barmode='stack')

    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), title=entidad)

    st.plotly_chart(fig)

    piv_tipo_gasto_entity = (filter_entity
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2024) en millones']
                      .sum()
                      .reset_index())


    st.subheader(f"Variación histórica por entidad: {entidad}")


    piv = filter_entity.pivot_table(index='Año',
                           values='Apropiación a precios constantes (2024) en millones',
                           aggfunc='sum'
                           )
    piv['pct'] = piv['Apropiación a precios constantes (2024) en millones'].pct_change()
    piv['pct'] = (piv['pct'] * 100).round(2)
    piv['CAGR'] = ((piv.loc[2024, 'Apropiación a precios constantes (2024) en millones'] / piv.loc[2013, 'Apropiación a precios constantes (2024) en millones']) ** (1/11)) - 1
    piv['CAGR'] = (piv['CAGR'] * 100).round(2)
    piv = piv.reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año')

    fig.add_trace(
        go.Bar(x=piv['Año'], y=piv['Apropiación a precios constantes (2024) en millones'],
               name='Apropiación a precios constantes (2024) en millones', marker_color=DIC_COLORES['ofiscal'][1]),
        row=1, col=1, 
    )

    fig.add_trace(go.Line(
            x=piv['Año'], 
            y=piv['pct'], 
            name='Variación porcentual (%)', line=dict(color=DIC_COLORES['ro_am_na'][1])
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Line(
            x=piv['Año'], y=piv['CAGR'], name='Variación anualizada (%)', line=dict(color=DIC_COLORES['verde'][0])
        ),
        row=1, col=2
    )
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1))

    st.plotly_chart(fig)
elif selected_option == "Treemap":
    st.header("Treemap")
    year = st.slider("Seleccione el año", 
                     min_value=min(years),
                     max_value=max(years))
    price = st.selectbox("Seleccione el nivel de precios",
                         prices.keys())
    filter_year = df[df['Año'] == year]

    dic_treemap = get_dic_colors(filter_year)
    dic_treemap['(?)'] = "#D9D9ED"
    fig = px.treemap(filter_year, 
                     path=[px.Constant('PGN'),     'Sector', 
                               'Entidad', 
                               'Tipo de gasto'],
                    values=prices[price],
                    color='Sector',
                    color_discrete_map=dic_treemap,
                    title="Matriz de composición de apropiación (en millones)")
    
    fig.update_layout(width=1000, height=600)
    
    st.plotly_chart(fig)
else:

    st.subheader("Descarga de dataset completo")


    binary_output = BytesIO()
    df.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar datos completos',
                    data = binary_output.getvalue(),
                    file_name = 'datos.xlsx')
    
    st.divider()

    # agregar la categoría todos al multiselect 
    #

    st.subheader("Descarga de dataset filtrado")
    col1, col2 = st.columns(2)
    with col1:
        sectors_2 = ['Todos'] + sectors
        sectors_selected = st.multiselect("Sector(es)", sectors_2)
        if "Todos" in sectors_selected:
            filter_ss = df[df['Sector'].isin(sectors)]
        else:
            filter_ss = df[df['Sector'].isin(sectors_selected)]


        entities_2 = ['Todas'] + list(filter_ss['Entidad'].unique())

        entities_selected = st.multiselect("Entidad(es)", entities_2)

        if "Todas" in entities_selected:
            entities_selected = list(filter_ss['Entidad'].unique())
        #rango de años
        years_2 = ['Todos'] + years
        years_selected = st.multiselect("Año(s)", years_2)

        if "Todos" in years_selected:
            years_selected = years.copy()

        filter_s_e_y = filter_ss[(filter_ss['Entidad'].isin(entities_selected)) & (filter_ss['Año'].isin(years_selected))]

    with col2:

        price_selected = st.selectbox("Nivel(es) de precios", prices.keys())
        total_or_account = st.selectbox("Suma o por cuenta", ["suma", "por cuenta"])
        if total_or_account == 'suma':
            pivot = (filter_s_e_y.groupby(['Año', 
                                          'Sector',
                                          'Entidad'])[prices[price_selected]]
                                          .sum()
                                          .reset_index())
        
        else:
            pivot = (filter_s_e_y.groupby(['Año', 
                                          'Sector',
                                          'Entidad','Tipo de gasto'])[prices[price_selected]]
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
        
    st.divider()
        
    st.subheader("Descarga del árbol sector-entidad del PGN")
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





   
