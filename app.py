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

from utils import DIC_COLORES, convert_df, get_dic_colors, get_dic_colors_area, create_dataframe_sankey

st.set_page_config(layout='wide', page_title="ofiscal - PePE", page_icon='imgs/favicon.jpeg')

df = pd.read_csv('gastos_def_2024.csv')
df2 = pd.read_csv('anteproyecto_2025.csv')
df['Apropiación a precios corrientes'] /= 1000000000
df['Apropiación a precios constantes (2024)'] /= 1000000000
years = list(df['Año'].unique())
years = [int(year) for year in years]
sectors = list(df['Sector'].unique())
entities = list(df['Entidad'].unique())
dict_gasto = {'Funcionamiento':DIC_COLORES['az_verd'][2],
              'Deuda':DIC_COLORES['ax_viol'][1],
              'Inversión':DIC_COLORES['ro_am_na'][3]}

show = False


prices = {"corrientes": 'Apropiación a precios corrientes',
          "constantes 2024": 'Apropiación a precios constantes (2024)'}

#with st.sidebar:
#    selected_option = option_menu("Menú", ["Main", "Histórico general", "Histórico por sector", "Histórico por entidad", "Treemap", "Descarga de datos"], 
#        icons=['arrow-right-short', 'file-bar-graph', 'intersect', "list-task", 'columns', 'cloud-download'], 
#        menu_icon="p", default_index=0, orientation="vertical")
st.image("imgs/transp.png")
st.divider()

selected_option = option_menu(None, ["Main", 
                                     "Histórico general", 
                                     "Histórico por sector", 
                                     "Histórico por entidad", 
                                     "Treemap", 
                                     "Descarga de datos",
                                     "Anteproyecto - 2025"], 
        icons=['arrow-right-short', 
               'file-bar-graph', 
               'intersect', 
               "list-task", 
               'columns', 
               'cloud-download',
               'pencil-square'], 
        menu_icon="p", default_index=0, orientation="horizontal")    
    

    
if selected_option == "Main":
    pass

elif selected_option == "Histórico general":

    st.header(selected_option)
    piv_2024 = df.groupby('Año')['Apropiación a precios constantes (2024)'].sum().reset_index()
    piv_corr = df.groupby('Año')['apropiacion_corrientes'].sum().reset_index()

    #piv_2024['Apropiación a precios constantes (2024)'] /= 1000

    fig = make_subplots(rows=1, cols=2, x_title='Año',  )
    
    fig.add_trace(
        go.Line(
            x=piv_2024['Año'], y=piv_2024['Apropiación a precios constantes (2024)'], 
            name='Apropiación a precios constantes (2024)', line=dict(color=DIC_COLORES['ax_viol'][1])
        ),
        row=1, col=1
    )

    piv_tipo_gasto = (df
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2024)']
                      .sum()
                      .reset_index())
    piv_tipo_gasto['total'] = piv_tipo_gasto.groupby(['Año'])['Apropiación a precios constantes (2024)'].transform('sum')

    piv_tipo_gasto['%'] = ((piv_tipo_gasto['Apropiación a precios constantes (2024)'] / piv_tipo_gasto['total']) * 100).round(2)

        
    for i, group in piv_tipo_gasto.groupby('Tipo de gasto'):
        fig.add_trace(go.Bar(
            x=group['Año'],
            y=group['%'],
            name=i, marker_color=dict_gasto[i]
        ), row=1, col=2)

    fig.update_layout(barmode='stack', hovermode='x unified')
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), title='Histórico general <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


    st.plotly_chart(fig)



    # distribución de gastos en las principales entidades (2024)
    # sectores con mayor asignación
    # entidades con mayor asignación 

elif selected_option == "Histórico por sector":

    st.header(selected_option)

    sector = st.selectbox("Seleccione el sector", sectors, key=2)
    filter_sector = df[df['Sector'] == sector]

    pivot_sector = filter_sector.pivot_table(index='Año', values=prices.values(), aggfunc='sum').reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año', shared_yaxes=True)
    
    fig.add_trace(
        go.Line(
            x=pivot_sector['Año'], y=pivot_sector['Apropiación a precios constantes (2024)'], 
            name='Apropiación a precios constantes (2024)', line=dict(color=DIC_COLORES['ax_viol'][1])
        ),
        row=1, col=1
    )

    piv_tipo_gasto_sector = (filter_sector
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2024)']
                      .sum()
                      .reset_index())
    for i, group in piv_tipo_gasto_sector.groupby('Tipo de gasto'):
        fig.add_trace(go.Bar(
            x=group['Año'],
            y=group['Apropiación a precios constantes (2024)'],
            name=i, marker_color=dict_gasto[i]
        ), row=1, col=2)

    fig.update_layout(barmode='stack', hovermode='x unified')


    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), title=f"{sector} <br><sup>Cifras en miles de millones de pesos</sup>", yaxis_tickformat='.0f')

    st.plotly_chart(fig)

    st.subheader(f"Variación histórica por sector: {sector}")



    pivot_sector = pivot_sector.set_index('Año')
    pivot_sector['pct'] = pivot_sector['Apropiación a precios constantes (2024)'].pct_change()
    pivot_sector['pct'] = (pivot_sector['pct'] * 100).round(2)
    den = max(pivot_sector.index) - min(pivot_sector.index)
    pivot_sector['CAGR'] = ((pivot_sector.loc[max(pivot_sector.index), 'Apropiación a precios constantes (2024)'] / pivot_sector.loc[min(pivot_sector.index), 'Apropiación a precios constantes (2024)']) ** (1/11)) - 1
    pivot_sector['CAGR'] = (pivot_sector['CAGR'] * 100).round(2)
    pivot_sector = pivot_sector.reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año')

    fig.add_trace(
            go.Bar(x=pivot_sector['Año'], y=pivot_sector['Apropiación a precios constantes (2024)'],
                name='Apropiación a precios constantes (2024)', marker_color=DIC_COLORES['ofiscal'][1]),
            row=1, col=1, 
        )

    fig.add_trace(go.Line(
                x=pivot_sector['Año'], 
                y=pivot_sector['pct'], 
                name='Variación porcentual (%)', line=dict(color=DIC_COLORES['ro_am_na'][1])
            ),
            row=1, col=2
        )
    fig.add_trace(
            go.Line(
                x=pivot_sector['Año'], y=pivot_sector['CAGR'], name='Variación anualizada (%)', line=dict(color=DIC_COLORES['verde'][0])
            ),
            row=1, col=2
        )
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1), hovermode='x unified', yaxis_tickformat='.0f', title=f"{sector} <br><sup>Cifras en miles de millones de pesos</sup>")

    st.plotly_chart(fig)
    




elif selected_option == "Histórico por entidad":


    st.header(selected_option)
    sector = st.selectbox("Seleccione el sector", sectors, key=3)
    filter_sector = df[df['Sector'] == sector]
 
    entities_sector = filter_sector['Entidad'].unique()
    entidad = st.selectbox("Seleccione la entidad",
                            entities_sector)
    
    filter_entity = filter_sector[filter_sector['Entidad'] == entidad]

    pivot_entity = filter_entity.pivot_table(index='Año',
                                           values=prices.values(),
                                           aggfunc='sum')
    
    pivot_entity = pivot_entity.reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año', shared_yaxes=True)
    
    fig.add_trace(
        go.Line(
            x=pivot_entity['Año'], y=pivot_entity['Apropiación a precios constantes (2024)'], 
            name='Apropiación a precios constantes (2024)', line=dict(color=DIC_COLORES['ax_viol'][1])
        ),
        row=1, col=1
    )
    piv_tipo_gasto_entity = (filter_entity
                      .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2024)']
                      .sum()
                      .reset_index())
    for i, group in piv_tipo_gasto_entity.groupby('Tipo de gasto'):
        fig.add_trace(go.Bar(
            x=group['Año'],
            y=group['Apropiación a precios constantes (2024)'],
            name=i, marker_color=dict_gasto[i]
        ), row=1, col=2)

    fig.update_layout(barmode='stack', hovermode='x unified')

    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), title=f"{entidad} <br><sup>Cifras en miles de millones de pesos</sup>", yaxis_tickformat='.0f')

    st.plotly_chart(fig)

    if pivot_entity['Año'].nunique() <=1:
        st.warning(f"La entidad {entidad} solo tiene información de un año.")
        st.stop()

    st.subheader(f"Variación histórica por entidad: {entidad}")

    pivot_entity = pivot_entity.set_index('Año')
    pivot_entity['pct'] = pivot_entity['Apropiación a precios constantes (2024)'].pct_change()
    pivot_entity['pct'] = (pivot_entity['pct'] * 100).round(2)
    den = max(pivot_entity.index) - min(pivot_entity.index)
    pivot_entity['CAGR'] = ((pivot_entity.loc[max(pivot_entity.index), 'Apropiación a precios constantes (2024)'] / pivot_entity.loc[min(pivot_entity.index), 'Apropiación a precios constantes (2024)'] ) ** (1/den)) - 1
    pivot_entity['CAGR'] = (pivot_entity['CAGR'] * 100).round(2)
    pivot_entity = pivot_entity.reset_index()

    fig = make_subplots(rows=1, cols=2, x_title='Año')

    fig.add_trace(
        go.Bar(x=pivot_entity['Año'], y=pivot_entity['Apropiación a precios constantes (2024)'],
               name='Apropiación a precios constantes (2024)', marker_color=DIC_COLORES['ofiscal'][1]),
        row=1, col=1, 
    )

    fig.add_trace(go.Line(
            x=pivot_entity['Año'], 
            y=pivot_entity['pct'], 
            name='Variación porcentual (%)', line=dict(color=DIC_COLORES['ro_am_na'][1])
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Line(
            x=pivot_entity['Año'], y=pivot_entity['CAGR'], name='Variación anualizada (%)', line=dict(color=DIC_COLORES['verde'][0])
        ),
        row=1, col=2
    )
    fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1), hovermode='x unified', yaxis_tickformat='.0f', title=f"{entidad} <br><sup>Cifras en miles de millones de pesos</sup>")

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
                    title="Matriz de composición anual del PGN <br><sup>Cifras en miles de millones de pesos</sup>")
    
    fig.update_layout(width=1000, height=600)
    
    st.plotly_chart(fig)

elif selected_option == "Anteproyecto - 2025":
    
    
    st.header("Anteproyecto - 2025")

    fig = px.treemap(df2, 
                            path=[px.Constant('Anteproyecto'), 'Sector', 'ENTIDAD','Tipo de gasto', 
                                    'CONCEPTO'],
                            values='TOTAL',
                            title="Matriz de composición anual del Anteproyecto <br><sup>Cifras en millones de pesos</sup>",
                            color_continuous_scale='Teal')
            
    fig.update_layout(width=1000, height=600)
            
    st.plotly_chart(fig)

    st.subheader("Flujo del gasto por tipo de gasto (% del PGN)")

    lista = ['PGN', 'Tipo de gasto', 'CONCEPTO']
    df3 = df2.copy()
    df3['PGN'] = 'PGN'

    dicti = {'2':['Inversion','Servicio de la deuda']}
    nodes, rev_info, links = create_dataframe_sankey(df3, 'TOTAL %',*lista, **dicti)
    fig = go.Figure(data=[go.Sankey(
    arrangement='snap',
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "#2635bf", width = 0.5),
      label = nodes['names'],
      color = nodes['color'],
      x = nodes['x_pos'].values ,
      y = nodes['x_pos'].values / 2.4
    ),
    link = dict(
      source = links['source'], 
      target = links['target'],
      value = links['value'],
      color = links['color'],
      hovertemplate='Proporción del gasto de %{source.label}<br />'+
        'hacia %{target.label}:<br /> <b>%{value:.2f}%<extra></extra>'
    ))])

    fig.update_layout(title_text="Flujo de gasto por sector - Top 10", 
                      font_size=12, 
                      width=1000, 
                      height=600)
    st.plotly_chart(fig)




    st.subheader("Flujo del gasto por sector (% del PGN)")
    lista = ['Sector', 'Tipo de gasto', 'CONCEPTO']

    top_10 = df2.groupby('Sector')['TOTAL'].sum().reset_index().sort_values(by='TOTAL', ascending=False).head(10)['Sector']

    top_10_df = df2[df2['Sector'].isin(top_10)]

    dicti = {'2':['Inversion','Servicio de la deuda']}
    nodes, rev_info, links = create_dataframe_sankey(top_10_df, 'TOTAL %',*lista, **dicti)
    fig = go.Figure(data=[go.Sankey(
    arrangement='snap',
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "#2635bf", width = 0.5),
      label = nodes['names'],
      color = nodes['color'],
      x = nodes['x_pos'].values ,
      y = nodes['x_pos'].values / 2.4
    ),
    link = dict(
      source = links['source'], 
      target = links['target'],
      value = links['value'],
      color = links['color'],
      hovertemplate='Proporción del gasto de %{source.label}<br />'+
        'hacia %{target.label}:<br /> <b>%{value:.2f}%<extra></extra>'
    ))])

    fig.update_layout(title_text="Flujo de gasto por sector - Top 10", 
                      font_size=12, 
                      width=1000, 
                      height=600)
    st.plotly_chart(fig)
    

    st.subheader("Flujo del gasto por entidad (% del PGN)")
    lista = ['ENTIDAD', 'Tipo de gasto', 'CONCEPTO']

    top_10 = df2.groupby('ENTIDAD')['TOTAL'].sum().reset_index().sort_values(by='TOTAL', ascending=False).head(10)['ENTIDAD']

    top_10_df = df2[df2['ENTIDAD'].isin(top_10)]

    dicti = {'2':['Inversion','Servicio de la deuda']}
    nodes, rev_info, links = create_dataframe_sankey(top_10_df, 'TOTAL %',*lista, **dicti)
    fig = go.Figure(data=[go.Sankey(
    arrangement='snap',
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "#2635bf", width = 0.5),
      label = nodes['names'],
      color = nodes['color'],
      x = nodes['x_pos'].values,
      y = nodes['x_pos'].values / 2.4
    ),
    link = dict(
      source = links['source'], 
      target = links['target'],
      value = links['value'],
      color = links['color'],
      hovertemplate='Proporción del gasto de %{source.label}<br />'+
        'hacia %{target.label}:<br /> <b>%{value:.2f}%<extra></extra>'
    ))])

    fig.update_layout(title_text="Flujo de gasto por entidad - Top 10", 
                      font_size=12, 
                      width=1000, 
                      height=600)
    st.plotly_chart(fig)

    st.subheader("Descarga de datos")


    binary_output = BytesIO()
    df2.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar datos de anteproyecto',
                    data = binary_output.getvalue(),
                    file_name = 'anteproyecto_2025.xlsx')    

    

else:
    st.header("Descarga de datos")

    st.subheader("Descarga de dataset completo")


    binary_output = BytesIO()
    df.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar datos completos',
                    data = binary_output.getvalue(),
                    file_name = 'datos.xlsx')

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





   
