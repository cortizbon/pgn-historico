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

df = pd.read_csv('datasets/gastos_def_2025_test.csv')       # gastos anuales
#df2 = pd.read_csv('datasets/datos_desagregados_2025.csv')   
pgn_25 = pd.read_csv('datasets/pgn_2025.csv')               # datos desagregados de pgn 25
df2025 = pd.read_excel('datasets/decreto_2025.xlsx')        # datos desagregados de decreto 2025
#diff = pd.read_excel('datasets/merge_william.xlsx')         # datos desagregados de diferencia
inc = pd.read_csv('datasets/ingresos_2025.csv')             # ingresos anuales
ejec = pd.read_csv('datasets/ejecucion_hist.csv')
rec = pd.read_csv('datasets/recaudo_hist.csv')
pib_rec = pd.read_csv('datasets/pib_rec.csv')
pib_rec2 = pd.read_csv('datasets/c2_pib_rec.csv')

inc['Valor_25_esc'] = (inc['Valor_25'] / 1_000_000_000).round(1)
df['Apropiación a precios corrientes'] /= 1_000_000_000
df['Apropiación a precios constantes (2025)'] /= 1_000_000_000

years = [int(year) for year in list(df['Año'].unique())]
sectors = list(df['Sector'].unique())
entities = list(df['Entidad'].unique())
dict_gasto = {'Funcionamiento':DIC_COLORES['az_verd'][2],
              'Deuda':DIC_COLORES['ax_viol'][1],
              'Inversión':DIC_COLORES['ro_am_na'][3]}

dict_ingreso = {'INGRESOS CORRIENTES DE LA NACIÓN':"white",
       'RECURSOS DE CAPITAL DE LA NACIÓN':"white", 
       'INGRESOS DE LOS ESTABLECIMIENTOS PÚBLICOS':DIC_COLORES['ro_am_na'][3],
       'CONTRIBUCIONES PARAFISCALES DE LA NACIÓN':"white",
       'FONDOS ESPECIALES DE LA NACIÓN':"white"}

dict_pat_ingreso = {'INGRESOS CORRIENTES DE LA NACIÓN':".",
       'RECURSOS DE CAPITAL DE LA NACIÓN':"x", 
       'INGRESOS DE LOS ESTABLECIMIENTOS PÚBLICOS':"",
       'CONTRIBUCIONES PARAFISCALES DE LA NACIÓN':"-",
       'FONDOS ESPECIALES DE LA NACIÓN':"+"}

show = False


prices = {"corrientes": 'Apropiación a precios corrientes',
          "constantes 2025": 'Apropiación a precios constantes (2025)'}

#with st.sidebar:
#    selected_option = option_menu("Menú", ["Main", "Histórico general", "Histórico por sector", "Histórico por entidad", "Treemap", "Descarga de datos"], 
#        icons=['arrow-right-short', 'file-bar-graph', 'intersect', "list-task", 'columns', 'cloud-download'], 
#        menu_icon="p", default_index=0, orientation="vertical")
st.image("imgs/transp.png")
st.divider()

selected_option = option_menu(None, ["Main", 
                                     "Ingresos", 
                                     "Gastos", 
                                     "Treemap", 
                                     "Coyuntura", 
                                     "Ejecución histórica",
                                     "Recaudo histórico",
                                     "PGN - 2025",
                                     "Descarga de datos"], 
        icons=['arrow-right-short', 
               'file-bar-graph', 
               'intersect', 
               'columns',
               "calendar3",
               "cart2", 
               'bag',
               'building-fill',
               'cloud-download'], 
        menu_icon="p", default_index=0, orientation="horizontal")    
    

    
if selected_option == "Main":
    pass

elif selected_option == 'Ingresos':
    tab1, tab2, tab3 = st.tabs(['General', 'Por sector', 'Por entidad'])

    with tab1:
        piv_year = inc.groupby('Año')['Valor_25_esc'].sum().reset_index()
        fig = make_subplots(rows=1, cols=2, x_title='Año',  )
        
        fig.add_trace(
            go.Line(
                x=piv_year['Año'], y=piv_year['Valor_25_esc'], 
                name='Ingreso', line=dict(color=DIC_COLORES['ax_viol'][1])
            ),
            row=1, col=1
        )

        piv_tipo_ingreso = (inc
                        .groupby(['Año', 'Ingreso_alt'])['Valor_25_esc']
                        .sum()
                        .reset_index())
        piv_tipo_ingreso['total'] = piv_tipo_ingreso.groupby(['Año'])['Valor_25_esc'].transform('sum')

        piv_tipo_ingreso['%'] = ((piv_tipo_ingreso['Valor_25_esc'] / piv_tipo_ingreso['total']) * 100).round(2)

        val = 0.2
        for i, group in piv_tipo_ingreso.groupby('Ingreso_alt'):
            fig.add_trace(go.Bar(
                x=group['Año'],
                y=group['%'],
                name=i, marker_color=dict_ingreso[i], 
                marker_pattern_shape=dict_pat_ingreso[i],
                marker_pattern_bgcolor=DIC_COLORES['az_verd'][2],
                marker_pattern_size=6,
                opacity=val
            ),  row=1, col=2)
            val += 0.2

        fig.update_layout(barmode='stack', hovermode='x unified')
        fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1), title='Histórico general <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


        st.plotly_chart(fig)  

        piv_year = inc.groupby(['Año', 'Ingreso_alt'])['Valor_25_esc'].sum().reset_index()
        fig = make_subplots(rows=1, cols=1, x_title='Año',  )

        for n, i in enumerate(piv_year['Ingreso_alt'].unique()):
            filtro = piv_year[piv_year['Ingreso_alt'] == i]       
            fig.add_trace(
                go.Line(
                    x=filtro['Año'], y=filtro['Valor_25_esc'], 
                    name=i, line=dict(color=DIC_COLORES['ro_am_na'][n]),
                ),
                row=1, col=1
            )
            print(n)  
        fig.update_layout(barmode='stack', hovermode='x unified')
        fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1), title='Histórico general <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')
        st.plotly_chart(fig)

    with tab2:
        d = inc[inc['Sector'] != 'Nación']
        sectors = d['Sector'].unique().tolist()
        sector = st.selectbox("Seleccione un sector: ", sectors, key=20)
        fil_sector = d[d['Sector'] == sector]
        piv_sec = fil_sector.groupby('Año')['Valor_25_esc'].sum().reset_index()

        fig = make_subplots(rows=1, cols=2, x_title='Año',  )
            
        fig.add_trace(
                go.Line(
                    x=piv_sec['Año'], y=piv_sec['Valor_25_esc'], 
                    name='Valor', line=dict(color=DIC_COLORES['ax_viol'][1])
                ),
                row=1, col=1
            )

        piv_sector = (fil_sector
                            .groupby(['Año', 'Ingreso específico'])['Valor_25_esc']
                            .sum()
                            .reset_index())

        piv_sector['total'] = piv_sector.groupby(['Año'])['Valor_25_esc'].transform('sum')

        piv_sector['%'] = ((piv_sector['Valor_25_esc'] / piv_sector['total']) * 100).round(2)

                
        for i, group in piv_sector.groupby('Ingreso específico'):
                fig.add_trace(go.Bar(
                    x=group['Año'],
                    y=group['%'],
                    name=i
                ), row=1, col=2)

        fig.update_layout(barmode='stack', hovermode='x unified')
        fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
            yanchor="bottom",
            y=-0.24,
            xanchor="right",
            x=1), title='Histórico por sector<br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


        st.plotly_chart(fig, key=1)

    with tab3:
        d = inc[inc['Sector'] != 'Nación']
        sector = st.selectbox("Seleccione un sector: ", sectors)
        d = d[d['Sector'] == sector]
        ents = d['Entidad'].unique().tolist()
        ent = st.selectbox("Seleccione una entidad: ", ents, key=4)
        fil_ent = d[d['Entidad'] == ent]
        piv_ent = fil_ent.groupby('Año')['Valor_25_esc'].sum().reset_index()

        fig = make_subplots(rows=1, cols=2, x_title='Año',  )
            
        fig.add_trace(
                go.Line(
                    x=piv_ent['Año'], y=piv_ent['Valor_25_esc'], 
                    name='Valor', line=dict(color=DIC_COLORES['ax_viol'][1])
                ),
                row=1, col=1
            )

        piv_entidad = (fil_ent
                            .groupby(['Año', 'Ingreso específico'])['Valor_25_esc']
                            .sum()
                            .reset_index())
        piv_entidad['total'] = piv_entidad.groupby(['Año'])['Valor_25_esc'].transform('sum')

        piv_entidad['%'] = ((piv_entidad['Valor_25_esc'] / piv_entidad['total']) * 100).round(2)

                
        for i, group in piv_entidad.groupby('Ingreso específico'):
                fig.add_trace(go.Bar(
                    x=group['Año'],
                    y=group['%'],
                    name=i
                ), row=1, col=2)

        fig.update_layout(barmode='stack', hovermode='x unified')
        fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
            yanchor="bottom",
            y=-0.24,
            xanchor="right",
            x=1), title='Histórico por entidad <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


        st.plotly_chart(fig, key=12)



elif selected_option == "Gastos":

    tab1, tab2, tab3 = st.tabs(['General',
                                'Por sector',
                                'Por entidad'])
    with tab1:

        piv_2024 = df.groupby('Año')['Apropiación a precios constantes (2025)'].sum().reset_index()
        tasa_gen_cagr = (piv_2024[piv_2024['Año'] == 2025]['Apropiación a precios constantes (2025)'].reset_index(drop=True)/ piv_2024[piv_2024['Año'] == 2013]['Apropiación a precios constantes (2025)'].reset_index(drop=True))[0] ** (1/(2025 - 2013)) - 1        
        piv_2024['CAGR'] = tasa_gen_cagr
        piv_corr = df.groupby('Año')['apropiacion_corrientes'].sum().reset_index()

        #piv_2024['Apropiación a precios constantes (2024)'] /= 1000

        fig = make_subplots(rows=1, cols=2, x_title='Año',  )
        
        fig.add_trace(
            go.Line(
                x=piv_2024['Año'], y=piv_2024['Apropiación a precios constantes (2025)'], 
                name='Apropiación a precios constantes (2025)', line=dict(color=DIC_COLORES['ax_viol'][1])
            ),
            row=1, col=1
        )

        piv_tipo_gasto = (df
                        .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2025)']
                        .sum()
                        .reset_index())
        piv_tipo_gasto['total'] = piv_tipo_gasto.groupby(['Año'])['Apropiación a precios constantes (2025)'].transform('sum')

        piv_tipo_gasto['%'] = ((piv_tipo_gasto['Apropiación a precios constantes (2025)'] / piv_tipo_gasto['total']) * 100).round(2)



            
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


        st.plotly_chart(fig, key=1)

    with tab2:

    

        sector = st.selectbox("Seleccione el sector", sectors, key=2)
        filter_sector = df[df['Sector'] == sector]

        pivot_sector = filter_sector.pivot_table(index='Año', values=prices.values(), aggfunc='sum').reset_index()

        fig = make_subplots(rows=1, cols=2, x_title='Año', shared_yaxes=True)
        
        fig.add_trace(
            go.Line(
                x=pivot_sector['Año'], y=pivot_sector['Apropiación a precios constantes (2025)'], 
                name='Apropiación a precios constantes (2025)', line=dict(color=DIC_COLORES['ax_viol'][1])
            ),
            row=1, col=1
        )

        piv_tipo_gasto_sector = (filter_sector
                        .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2025)']
                        .sum()
                        .reset_index())
        for i, group in piv_tipo_gasto_sector.groupby('Tipo de gasto'):
            fig.add_trace(go.Bar(
                x=group['Año'],
                y=group['Apropiación a precios constantes (2025)'],
                name=i, marker_color=dict_gasto[i]
            ), row=1, col=2)

        fig.update_layout(barmode='stack', hovermode='x unified')


        fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1), title=f"{sector} <br><sup>Cifras en miles de millones de pesos</sup>", yaxis_tickformat='.0f')

        st.plotly_chart(fig, key=20)

        st.subheader(f"Variación histórica por sector: {sector}")



        pivot_sector = pivot_sector.set_index('Año')
        pivot_sector['pct'] = pivot_sector['Apropiación a precios constantes (2025)'].pct_change()
        pivot_sector['pct'] = (pivot_sector['pct'] * 100).round(2)
        den = max(pivot_sector.index) - min(pivot_sector.index)
        pivot_sector['CAGR'] = ((pivot_sector.loc[max(pivot_sector.index), 'Apropiación a precios constantes (2025)'] / pivot_sector.loc[min(pivot_sector.index), 'Apropiación a precios constantes (2025)']) ** (1/11)) - 1
        pivot_sector['CAGR'] = (pivot_sector['CAGR'] * 100).round(2)
        pivot_sector['CAGR_gen'] = (tasa_gen_cagr * 100).round(2)
        pivot_sector = pivot_sector.reset_index()

        fig = make_subplots(rows=1, cols=2, x_title='Año')

        fig.add_trace(
                go.Bar(x=pivot_sector['Año'], y=pivot_sector['Apropiación a precios constantes (2025)'],
                    name='Apropiación a precios constantes (2025)', marker_color=DIC_COLORES['ofiscal'][1]),
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
                    x=pivot_sector['Año'], y=pivot_sector['CAGR'], name='Variación anualizada sector (%)', line=dict(color=DIC_COLORES['verde'][0])
                ),
                row=1, col=2
            )
        fig.add_trace(
                go.Line(
                    x=pivot_sector['Año'], y=pivot_sector['CAGR_gen'], name='Variación anualizada PGN (%)', line=dict(color=DIC_COLORES['ax_viol'][2])
                ),
                row=1, col=2
            )
        fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1), hovermode='x unified', yaxis_tickformat='.0f', title=f"{sector} <br><sup>Cifras en miles de millones de pesos</sup>")

        st.plotly_chart(fig, key=30)

    with tab3:
    
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
                x=pivot_entity['Año'], y=pivot_entity['Apropiación a precios constantes (2025)'], 
                name='Apropiación a precios constantes (2025)', line=dict(color=DIC_COLORES['ax_viol'][1])
            ),
            row=1, col=1
        )
        piv_tipo_gasto_entity = (filter_entity
                        .groupby(['Año', 'Tipo de gasto'])['Apropiación a precios constantes (2025)']
                        .sum()
                        .reset_index())
        for i, group in piv_tipo_gasto_entity.groupby('Tipo de gasto'):
            fig.add_trace(go.Bar(
                x=group['Año'],
                y=group['Apropiación a precios constantes (2025)'],
                name=i, marker_color=dict_gasto[i]
            ), row=1, col=2)

        fig.update_layout(barmode='stack', hovermode='x unified')

        fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1), title=f"{entidad} <br><sup>Cifras en miles de millones de pesos</sup>", yaxis_tickformat='.0f')

        st.plotly_chart(fig, key=40)

        if pivot_entity['Año'].nunique() <=1:
            st.warning(f"La entidad {entidad} solo tiene información de un año.")
            st.stop()

        st.subheader(f"Variación histórica por entidad: {entidad}")

        pivot_entity = pivot_entity.set_index('Año')
        pivot_entity['pct'] = pivot_entity['Apropiación a precios constantes (2025)'].pct_change()
        pivot_entity['pct'] = (pivot_entity['pct'] * 100).round(2)
        den = max(pivot_entity.index) - min(pivot_entity.index)
        pivot_entity['CAGR'] = ((pivot_entity.loc[max(pivot_entity.index), 'Apropiación a precios constantes (2025)'] / pivot_entity.loc[min(pivot_entity.index), 'Apropiación a precios constantes (2025)'] ) ** (1/den)) - 1
        pivot_entity['CAGR'] = (pivot_entity['CAGR'] * 100).round(2)
        pivot_entity['CAGR_gen'] = (tasa_gen_cagr * 100).round(2)
        pivot_entity = pivot_entity.reset_index()

        fig = make_subplots(rows=1, cols=2, x_title='Año')

        fig.add_trace(
            go.Bar(x=pivot_entity['Año'], y=pivot_entity['Apropiación a precios constantes (2025)'],
                name='Apropiación a precios constantes (2025)', marker_color=DIC_COLORES['ofiscal'][1]),
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
        fig.add_trace(
                go.Line(
                    x=pivot_entity['Año'], y=pivot_entity['CAGR_gen'], name='Variación anualizada PGN (%)', line=dict(color=DIC_COLORES['ax_viol'][2])
                ),
                row=1, col=2
            )
        fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1), hovermode='x unified', yaxis_tickformat='.0f', title=f"{entidad} <br><sup>Cifras en miles de millones de pesos</sup>")

        st.plotly_chart(fig, key=50)

elif selected_option == "Treemap":

    tab1, tab2 = st.tabs(['Ingreso', 'Gasto'])
    with tab1:

        year = st.slider("Seleccione el año (ingreso)", 
                        min_value=min(years),
                        max_value=max(years))
        filter_inc = inc[inc['Año'] == year]

        fig = px.treemap(filter_inc, 
                        path=[px.Constant('PGN'),     'Ingreso', 
                                'Ingreso específico'],
                        values='Valor_25_esc',
                        color_discrete_sequence=[DIC_COLORES['ax_viol'][1],
                                                 DIC_COLORES['ro_am_na'][3],
                                                 DIC_COLORES['az_verd'][2]],
                        title="Matriz de composición anual de ingreso del PGN <br><sup>Cifras en miles de millones de pesos</sup>")
        
        fig.update_layout(width=1000, height=600)
        
        st.plotly_chart(fig)

    with tab2:
        year = st.slider("Seleccione el año", 
                        min_value=min(years),
                        max_value=max(years))

        filter_year = df[df['Año'] == year]
    

        dic_treemap = get_dic_colors(filter_year)
        dic_treemap['(?)'] = "#D9D9ED"
        fig = px.treemap(filter_year, 
                        path=[px.Constant('PGN'),     'Sector', 
                                'Entidad', 
                                'Tipo de gasto'],
                        values='Apropiación a precios constantes (2025)',
                        color='Sector',
                        color_discrete_map=dic_treemap,
                        title="Matriz de composición anual de gasto del PGN <br><sup>Cifras en miles de millones de pesos</sup>")
        
        fig.update_layout(width=1000, height=600)
    
        st.plotly_chart(fig)

elif selected_option == 'Coyuntura':
    tab1, tab2 = st.tabs(['Ejecución', 'Recaudo'])
    with tab1:
        #st.warning("Sin datos de ejecución a la fecha. Esperando actualización de Minhacienda.")
        
        months = [
            "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
        ]
        df_ejec = pd.read_csv('datasets/ejec_acum_2025.csv')
        # general

        a = (df_ejec['APR. VIGENTE'].sum() / 1_000_000_000_000).round(2)
        b = ((df_ejec['COMPROMISO'].sum() / df_ejec['APR. VIGENTE'].sum()) * 100).round(1)
        c = ((df_ejec['OBLIGACION'].sum() / df_ejec['APR. VIGENTE'].sum() ) * 100).round(1)

        t1, t2 = st.tabs(["Vista general",
                                    "Navegación detallada"])

        with t1:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Apr. Vigente (bil)", a)
            with col2: 
                st.metric("% Comprometido", f"{b}%")
            with col3:
                st.metric("% Ejecutado ", f"{c}%")
            with col4:
                st.metric("% Proyección de ejecución final", f"{round(c * 12, 1)}%")

            tab = df_ejec.pivot_table(index='mes',
                                    values=['APR. VIGENTE', 'OBLIGACION', 'COMPROMISO'],
                                    aggfunc='sum')

            num_month = len(tab)

            
            fig = make_subplots(rows=1, cols=2, subplot_titles=("Valores (billones)", "Porcentaje (%)"))

            if num_month == 1:
                comp_rate = (tab['COMPROMISO'] / tab['APR. VIGENTE'])[0] 
                obl_rate = (tab['OBLIGACION'] / tab['APR. VIGENTE'])[0]
                obs_values_r = [obl_rate]
            else:
                prov_tab = tab.pct_change().fillna(tab.iloc[0].div(tab['APR. VIGENTE'].unique()[0]))
                comp_rate = prov_tab['COMPROMISO'].mean()
                obl_rate = prov_tab['OBLIGACION'].mean()
                obs_values_r = prov_tab['OBLIGACION'].tolist()
            
            obs_values_v = tab['OBLIGACION'].tolist()
            
            forecast_values = [obl_rate * i  for i in range(num_month + 1, 13)]
            full_values_ej = obs_values_r + forecast_values
            full_values_ej = [ round(i * 100, 2) for i in full_values_ej]
            fig.add_trace(go.Scatter(x=months[:num_month + 1], 
                                        y=full_values_ej[:num_month + 1], 
                                        mode='lines+markers',
                                        name='Ejecutado', showlegend=False,
                                        line=dict(color='#dd722a')), row=1, col=2)

                # Highlight the forecasted part with a red dashed line (the last 4 points)
            fig.add_trace(go.Scatter(
                    x=months[num_month:],  # x-axis for forecasted values
                    y=full_values_ej[num_month:],     # The forecasted values
                    mode='lines+markers',          # Just lines (no markers here)
                    name='Pronóstico', 
                    line=dict(color='#81D3CD', width=2, dash='dash'),
                    marker=dict(color='#81D3CD', size=8),  # Dashed line for forecast
                ), row=1, col=2)
            perd_aprop = 100 - full_values_ej[-1]


            forecast_values = [obl_rate * i for i in range(num_month + 1, 13)]
            forecast_values = [tab['APR. VIGENTE'].unique()[0] * i for i in forecast_values]
            full_values_ej = obs_values_v + forecast_values
            full_values_ej = [round(i / 1_000_000_000, 1) for i in full_values_ej]


            fig.add_trace(go.Scatter(x=months[:num_month + 1], 
                                        y=full_values_ej[:num_month + 1], 
                                        mode='lines+markers', 
                                        name='Ejecutado', showlegend=False,
                                        line=dict(color='#2635bf')), row=1, col=1)
            fig.add_trace(go.Scatter(
                    x=months[num_month:],  # x-axis for forecasted values
                    y=full_values_ej[num_month:],     # The forecasted values
                    mode='lines+markers',          # Just lines (no markers here)
                    name='Pronóstico', showlegend=False,
                    line=dict(color='#81D3CD', width=2, dash='dash'),
                    marker=dict(color='#81D3CD', size=8),  # Dashed line for forecast
                ), row=1, col=1)

            fig.add_shape(type='line', x0=0, x1=11, y0=round(tab['APR. VIGENTE'].unique()[0] / (1_000_000_000), 1), y1=round(tab['APR. VIGENTE'].unique()[0] / (1_000_000_000), 1), line=dict(color='#2635bf', dash='dash'),
                            row=1, col=1)
            
            fig.add_shape(type='line', x0=0, x1=11, y0=100, y1=100, line=dict(color='#2635bf', dash='dash'),
                            row=1, col=2)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig)

            
            if perd_aprop > 0:
                    st.error(f"Puede presentarse una pérdida de apropiación del {round(perd_aprop, 2)}%.")
            else:
                    st.success(f"No hay pérdida de apropiación.")

        with t2:
            st.subheader('Por sector')
            sectores = df_ejec['Sector'].unique().tolist()
            sector = st.selectbox('Seleccione un sector: ', sectores)
            f_sec = df_ejec[df_ejec['Sector'] == sector]

            a = (f_sec['APR. VIGENTE'].sum() / 1_000_000_000).round(2)
            b = ((f_sec['COMPROMISO'].sum() / f_sec['APR. VIGENTE'].sum()) * 100).round(1)
            c = ((f_sec['OBLIGACION'].sum() / f_sec['APR. VIGENTE'].sum() ) * 100).round(1)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Apr. Vigente (mmil)", a)
            with col2: 
                st.metric("% Comprometido", f"{b}%")
            with col3:
                st.metric("% Ejecutado ", f"{c}%")
            with col4:
                st.metric("% Proyección de ejecución final", f"{round(c * 12, 1)}%")

            tab = f_sec.pivot_table(index='mes',
                                    values=['APR. VIGENTE', 'OBLIGACION', 'COMPROMISO'],
                                    aggfunc='sum')

            num_month = len(tab)

            
            fig = make_subplots(rows=1, cols=2, subplot_titles=("Valores (billones)", "Porcentaje (%)"))

            if num_month == 1:
                comp_rate = (tab['COMPROMISO'] / tab['APR. VIGENTE'])[0] 
                obl_rate = (tab['OBLIGACION'] / tab['APR. VIGENTE'])[0]
                obs_values_r = [obl_rate]
            else:
                prov_tab = tab.pct_change().fillna(tab.iloc[0].div(tab['APR. VIGENTE'].unique()[0]))
                comp_rate = prov_tab['COMPROMISO'].mean()
                obl_rate = prov_tab['OBLIGACION'].mean()
                obs_values_r = prov_tab['OBLIGACION'].tolist()
            
            obs_values_v = tab['OBLIGACION'].tolist()
            
            forecast_values = [obl_rate * i  for i in range(num_month + 1, 13)]
            full_values_ej = obs_values_r + forecast_values
            full_values_ej = [ round(i * 100, 2) for i in full_values_ej]
            fig.add_trace(go.Scatter(x=months[:num_month + 1], 
                                        y=full_values_ej[:num_month + 1], 
                                        mode='lines+markers',
                                        name='Ejecutado', showlegend=False,
                                        line=dict(color='#dd722a')), row=1, col=2)

                # Highlight the forecasted part with a red dashed line (the last 4 points)
            fig.add_trace(go.Scatter(
                    x=months[num_month:],  # x-axis for forecasted values
                    y=full_values_ej[num_month:],     # The forecasted values
                    mode='lines+markers',          # Just lines (no markers here)
                    name='Pronóstico', 
                    line=dict(color='#81D3CD', width=2, dash='dash'),
                    marker=dict(color='#81D3CD', size=8),  # Dashed line for forecast
                ), row=1, col=2)
            perd_aprop = 100 - full_values_ej[-1]


            forecast_values = [obl_rate * i for i in range(num_month + 1, 13)]
            forecast_values = [tab['APR. VIGENTE'].unique()[0] * i for i in forecast_values]
            full_values_ej = obs_values_v + forecast_values
            full_values_ej = [round(i / 1_000_000_000, 1) for i in full_values_ej]


            fig.add_trace(go.Scatter(x=months[:num_month + 1], 
                                        y=full_values_ej[:num_month + 1], 
                                        mode='lines+markers', 
                                        name='Ejecutado', showlegend=False,
                                        line=dict(color='#2635bf')), row=1, col=1)
            fig.add_trace(go.Scatter(
                    x=months[num_month:],  # x-axis for forecasted values
                    y=full_values_ej[num_month:],     # The forecasted values
                    mode='lines+markers',          # Just lines (no markers here)
                    name='Pronóstico', showlegend=False,
                    line=dict(color='#81D3CD', width=2, dash='dash'),
                    marker=dict(color='#81D3CD', size=8),  # Dashed line for forecast
                ), row=1, col=1)

            fig.add_shape(type='line', x0=0, x1=11, y0=round(tab['APR. VIGENTE'].unique()[0] / (1_000_000_000), 1), y1=round(tab['APR. VIGENTE'].unique()[0] / (1_000_000_000), 1), line=dict(color='#2635bf', dash='dash'),
                            row=1, col=1)
            
            fig.add_shape(type='line', x0=0, x1=11, y0=100, y1=100, line=dict(color='#2635bf', dash='dash'),
                            row=1, col=2)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig)

            
            if perd_aprop > 0:
                    st.error(f"Puede presentarse una pérdida de apropiación del {round(perd_aprop, 2)}% en el sector {sector}.")
            else:
                    st.success(f"No hay pérdida de apropiación en el sector {sector}.")

            mes = max(f_sec['mes_num'].unique())

            piv = (df_ejec[df_ejec['mes_num'] == 1].pivot_table(index='Sector',
                                                           values=['APR. VIGENTE', 'OBLIGACION'],
                                                           aggfunc='sum')
                                                           .assign(perc_ejec=lambda x: (x['OBLIGACION'] / x['APR. VIGENTE']).mul(100).round(2))
                                                           .sort_values(by='perc_ejec', ascending=False))
            best = piv.head(5).reset_index().sort_values(by='perc_ejec').reset_index(drop=True).set_index('Sector')
            worst = piv.tail(5).reset_index().sort_values(by='perc_ejec').reset_index(drop=True).set_index('Sector')
            st.dataframe(best)
            st.dataframe(worst)

            fig = make_subplots(rows=1, cols=2, subplot_titles=("Top 5 mejores", "Top 5 peores"))

            fig_bar1 = px.bar(best, 
                              x='perc_ejec', 
                              orientation="h", 
                              hover_data=['perc_ejec'], 
                              color_discrete_sequence=['#81D3CD'])
            fig_bar2 = px.bar(worst, 
                              x='perc_ejec', 
                              orientation='h', 
                              hover_data=['perc_ejec'], 
                              color_discrete_sequence=['#81D3CD'])

            for d in fig_bar1.data:
                fig.add_trace(d, row=1, col=1)
            for d in fig_bar2.data:
                fig.add_trace(d, row=1, col=2)


            fig.update_layout(yaxis1=dict(showticklabels=False),
                              yaxis2=dict(showticklabels=False),
                                xaxis1=dict(title="%"), 
                                xaxis2=dict(title="%"))   

            st.plotly_chart(fig)

            
            st.subheader('Por entidad')
            sector = st.selectbox("Seleccione un sector: ", sectores, key=124)
            f_sec = df_ejec[df_ejec['Sector'] == sector]
            ents = f_sec['Entidad'].unique().tolist()
            ent = st.selectbox('Seleccione una entidad: ', ents)
            f_ent = f_sec[f_sec['Entidad'] == ent]

            a = (f_ent['APR. VIGENTE'].sum() / 1_000_000_000).round(2)
            b = ((f_ent['COMPROMISO'].sum() / f_ent['APR. VIGENTE'].sum()) * 100).round(1)
            c = ((f_ent['OBLIGACION'].sum() / f_ent['APR. VIGENTE'].sum() ) * 100).round(1)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Apr. Vigente (mmil)", a)
            with col2: 
                st.metric("% Comprometido", f"{b}%")
            with col3:
                st.metric("% Ejecutado ", f"{c}%")
            with col4:
                st.metric("% Proyección de ejecución final", f"{round(c * 12, 1)}%")

            tab = f_ent.pivot_table(index='mes',
                                    values=['APR. VIGENTE', 'OBLIGACION', 'COMPROMISO'],
                                    aggfunc='sum')

            num_month = len(tab)

            
            fig = make_subplots(rows=1, cols=2, subplot_titles=("Valores (billones)", "Porcentaje (%)"))

            if num_month == 1:
                comp_rate = (tab['COMPROMISO'] / tab['APR. VIGENTE'])[0] 
                obl_rate = (tab['OBLIGACION'] / tab['APR. VIGENTE'])[0]
                obs_values_r = [obl_rate]
            else:
                prov_tab = tab.pct_change().fillna(tab.iloc[0].div(tab['APR. VIGENTE'].unique()[0]))
                comp_rate = prov_tab['COMPROMISO'].mean()
                obl_rate = prov_tab['OBLIGACION'].mean()
                obs_values_r = prov_tab['OBLIGACION'].tolist()
            
            obs_values_v = tab['OBLIGACION'].tolist()
            
            forecast_values = [obl_rate * i  for i in range(num_month + 1, 13)]
            full_values_ej = obs_values_r + forecast_values
            full_values_ej = [ round(i * 100, 2) for i in full_values_ej]
            fig.add_trace(go.Scatter(x=months[:num_month + 1], 
                                        y=full_values_ej[:num_month + 1], 
                                        mode='lines+markers',
                                        name='Ejecutado', showlegend=False,
                                        line=dict(color='#dd722a')), row=1, col=2)

                # Highlight the forecasted part with a red dashed line (the last 4 points)
            fig.add_trace(go.Scatter(
                    x=months[num_month:],  # x-axis for forecasted values
                    y=full_values_ej[num_month:],     # The forecasted values
                    mode='lines+markers',          # Just lines (no markers here)
                    name='Pronóstico', 
                    line=dict(color='#81D3CD', width=2, dash='dash'),
                    marker=dict(color='#81D3CD', size=8),  # Dashed line for forecast
                ), row=1, col=2)
            perd_aprop = 100 - full_values_ej[-1]


            forecast_values = [obl_rate * i for i in range(num_month + 1, 13)]
            forecast_values = [tab['APR. VIGENTE'].unique()[0] * i for i in forecast_values]
            full_values_ej = obs_values_v + forecast_values
            full_values_ej = [round(i / 1_000_000_000, 1) for i in full_values_ej]


            fig.add_trace(go.Scatter(x=months[:num_month + 1], 
                                        y=full_values_ej[:num_month + 1], 
                                        mode='lines+markers', 
                                        name='Ejecutado', showlegend=False,
                                        line=dict(color='#2635bf')), row=1, col=1)
            fig.add_trace(go.Scatter(
                    x=months[num_month:],  # x-axis for forecasted values
                    y=full_values_ej[num_month:],     # The forecasted values
                    mode='lines+markers',          # Just lines (no markers here)
                    name='Pronóstico', showlegend=False,
                    line=dict(color='#81D3CD', width=2, dash='dash'),
                    marker=dict(color='#81D3CD', size=8),  # Dashed line for forecast
                ), row=1, col=1)

            fig.add_shape(type='line', x0=0, x1=11, y0=round(tab['APR. VIGENTE'].unique()[0] / (1_000_000_000), 1), y1=round(tab['APR. VIGENTE'].unique()[0] / (1_000_000_000), 1), line=dict(color='#2635bf', dash='dash'),
                            row=1, col=1)
            
            fig.add_shape(type='line', x0=0, x1=11, y0=100, y1=100, line=dict(color='#2635bf', dash='dash'),
                            row=1, col=2)
            
            fig.update_layout(showlegend=False)
            
            st.plotly_chart(fig, key=100)
        

            
            if perd_aprop > 0:
                    st.error(f"Puede presentarse una pérdida de apropiación del {round(perd_aprop, 2)}% en la entidad {ent}.")
            else:
                    st.success(f"No hay pérdida de apropiación en la entidad {ent}.")

            piv = (df_ejec[df_ejec['mes_num'] == 1].pivot_table(index='Entidad',
                                                           values=['APR. VIGENTE', 'OBLIGACION'],
                                                           aggfunc='sum')
                                                           .assign(perc_ejec=lambda x: (x['OBLIGACION'] / x['APR. VIGENTE']).mul(100).round(2))
                                                           .sort_values(by='perc_ejec', ascending=False))
            best = piv.head(10).reset_index().sort_values(by='perc_ejec').reset_index(drop=True).set_index('Entidad')
            worst = piv.tail(10).reset_index().sort_values(by='perc_ejec').reset_index(drop=True).set_index('Entidad')
            worst['perc_ejec'] += 0.00001

            fig = make_subplots(rows=1, cols=2, subplot_titles=("Top 10 mejores", "Top 10 peores"))

            fig_bar1 = px.bar(best, 
                              x='perc_ejec', 
                              orientation="h", 
                              hover_data=['perc_ejec'], 
                              color_discrete_sequence=['#dd722a'])
            fig_bar2 = px.bar(worst, 
                              x='perc_ejec', 
                              orientation='h', 
                              hover_data=['perc_ejec'], 
                              color_discrete_sequence=['#dd722a'])

            for d in fig_bar1.data:
                fig.add_trace(d, row=1, col=1)
            for d in fig_bar2.data:
                fig.add_trace(d, row=1, col=2)


            fig.update_layout(yaxis1=dict(showticklabels=False),
                              yaxis2=dict(showticklabels=False),
                                xaxis1=dict(title="%"), 
                                xaxis2=dict(title="%"))   

            st.plotly_chart(fig)
            

    with tab2:
        st.warning("Sin datos de recaudo a la fecha. Esperando actualización de DIAN.")

        time2 = """rec = pd.read_csv('datasets/recaudo.csv')
        rec['Valor'] = rec['Valor'] / 1_000

        tab1, tab2, tab3 = st.tabs(['General', 'Interno', 'Externo'])

        with tab1:
            piv_year = rec.groupby(['Mes_num', 'Mes'])['Valor'].sum().reset_index()
            acum = (piv_year
                                            .groupby(['Mes_num', 'Mes'])['Valor']
                                            .sum()
                                            .reset_index()
                                            .assign(Acumulado=lambda x: x['Valor'].cumsum()))[['Mes','Acumulado']]
            fig = make_subplots(rows=1, cols=2, x_title='Año',  )
            
            fig.add_trace(
                    go.Scatter(
                    x=acum['Mes'],  # x-axis for forecasted values
                    y=acum['Acumulado'],     # The forecasted values
                    mode='lines+markers',          # Just lines (no markers here)
                    name='Recaudo acumulado', showlegend=True,
                    line=dict(color=DIC_COLORES['ax_viol'][1], width=2, dash='dash'),
                    marker=dict(color=DIC_COLORES['ax_viol'][1], size=8),  # Dashed line for forecast
                ), row=1, col=1
                )

            piv_recaudo = (rec
                            .groupby(['Mes_num','Mes', 'Tipo de impuesto'])['Valor']
                            .sum()
                            .reset_index())
            piv_recaudo['total'] = piv_recaudo.groupby(['Mes_num'])['Valor'].transform('sum')

            piv_recaudo['%'] = ((piv_recaudo['Valor'] / piv_recaudo['total']) * 100).round(2)
            dict_rec = {'Interno':DIC_COLORES['az_verd'][2],
                'Externo':DIC_COLORES['ax_viol'][1],
                'Por clasificar':DIC_COLORES['ro_am_na'][3]}

            for i, group in piv_recaudo.groupby('Tipo de impuesto'):
                fig.add_trace(go.Bar(
                    x=group['Mes'],
                    y=group['%'],
                    name=i, marker_color=dict_rec[i],
                ),  row=1, col=2)


            fig.update_layout(barmode='stack', hovermode='x unified')
            fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1), title='Histórico general <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


            st.plotly_chart(fig)  

            
        with tab2:
                rec_int = rec[rec['Tipo de impuesto'] == 'Interno']
                piv_recaudo = (rec_int
                                .groupby(['Mes_num','Mes', 'clas_alt'])['Valor']
                                .sum()
                                .reset_index())
                acum = (piv_recaudo
                                            .groupby(['Mes_num', 'Mes'])['Valor']
                                            .sum()
                                            .reset_index()
                                            .assign(Acumulado=lambda x: x['Valor'].cumsum()))[['Mes','Acumulado']]
                piv_recaudo['total'] = piv_recaudo.groupby(['Mes_num'])['Valor'].transform('sum')

                piv_recaudo['%'] = ((piv_recaudo['Valor'] / piv_recaudo['total']) * 100).round(2)
                fig = make_subplots(rows=1, cols=2, x_title='Año',  )
            
                fig.add_trace(
                    go.Scatter(
                    x=acum['Mes'],  # x-axis for forecasted values
                    y=acum['Acumulado'],     # The forecasted values
                    mode='lines+markers',          # Just lines (no markers here)
                    name='Recaudo acumulado', showlegend=True,
                    line=dict(color=DIC_COLORES['ax_viol'][1], width=2, dash='dash'),
                    marker=dict(color=DIC_COLORES['ax_viol'][1], size=8),  # Dashed line for forecast
                ), row=1, col=1
                )
                dict_alt = {'IVA Interno':DIC_COLORES['az_verd'][2],
                'Renta':DIC_COLORES['ax_viol'][1],
                'Otros':DIC_COLORES['ro_am_na'][3]}

                for i, group in piv_recaudo.groupby('clas_alt'):
                    fig.add_trace(go.Bar(
                        x=group['Mes'],
                        y=group['%'],
                        name=i, marker_color=dict_alt[i]
                    ),  row=1, col=2)


                fig.update_layout(barmode='stack', hovermode='x unified')
                fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1), title='Histórico interno <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


                st.plotly_chart(fig)

        with tab3:
                rec_ext = rec[rec['Tipo de impuesto'] == 'Externo']
                piv_recaudo = (rec_ext
                                .groupby(['Mes_num','Mes', 'Clasificación'])['Valor']
                                .sum()
                                .reset_index())
                acum = (piv_recaudo
                                            .groupby(['Mes_num', 'Mes'])['Valor']
                                            .sum()
                                            .reset_index()
                                            .assign(Acumulado=lambda x: x['Valor'].cumsum()))[['Mes','Acumulado']]
                piv_recaudo['total'] = piv_recaudo.groupby(['Mes_num'])['Valor'].transform('sum')

                piv_recaudo['%'] = ((piv_recaudo['Valor'] / piv_recaudo['total']) * 100).round(2)
                fig = make_subplots(rows=1, cols=2, x_title='Año',  )
            
                fig.add_trace(
                    go.Scatter(
                    x=acum['Mes'],  # x-axis for forecasted values
                    y=acum['Acumulado'],     # The forecasted values
                    mode='lines+markers',          # Just lines (no markers here)
                    name='Recaudo acumulado', showlegend=True,
                    line=dict(color=DIC_COLORES['ax_viol'][1], width=2, dash='dash'),
                    marker=dict(color=DIC_COLORES['ax_viol'][1], size=8),  # Dashed line for forecast
                ), row=1, col=1
                )
                dict_alt = {'IVA Externo ':DIC_COLORES['ro_am_na'][3],
                'Arancel':DIC_COLORES['az_verd'][2]}
                for i, group in piv_recaudo.groupby('Clasificación'):
                    fig.add_trace(go.Bar(
                        x=group['Mes'],
                        y=group['%'],
                        name=i, marker_color=dict_alt[i]
                    ),  row=1, col=2)


                fig.update_layout(barmode='stack', hovermode='x unified')
                fig.update_layout(width=1000, height=500, legend=dict(orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1), title='Histórico externo <br><sup>Cifras en miles de millones de pesos</sup>', yaxis_tickformat='.0f')


                st.plotly_chart(fig)"""
    
elif selected_option == 'Ejecución histórica':

    l_sectores = ejec['Sector'].unique().tolist()
    st.header("Ejecución histórica")

    st.subheader("General")

    t = ejec.pivot_table(index='Año',
                        columns='Etapa',
                        values='Valor_pc',
                        aggfunc='sum')
    tab = t.div(t['Apropiación'], axis=0).mul(100).round(1).reset_index()
    t = t.reset_index()

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Ejecución", "%"))
    
    fig_area = go.Figure()

    # Add traces
    fig_area.add_trace(go.Scatter(x=tab["Año"], 
                             y=tab["Apropiación"], 
                             fill='tozeroy',
                             mode='none', 
                             name='Apropiación',
                             fillcolor="#2635bf")
                             )
    fig_area.add_trace(go.Scatter(x=tab["Año"], 
                             y=tab["Compromiso"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Compromiso',
                             fillcolor="#F7B261"))
    fig_area.add_trace(go.Scatter(x=tab["Año"], 
                             y=tab["Obligación"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Obligación',
                             fillcolor="#009999"))
    fig_area.add_trace(go.Scatter(x=tab["Año"], 
                             y=tab["Pago"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Pago',
                             fillcolor="#81D3CD"))

    # Customize layout
    fig_area.update_layout(
        title="Ejecución histórica",
        xaxis_title="Año",
        yaxis_title="Valor",
        template="plotly_white")
    

    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(x=t["Año"], 
                             y=t["Apropiación"], 
                             fill='tozeroy',
                             mode='none', 
                             name='Apropiación',
                             fillcolor="#2635bf"))
    fig_line.add_trace(go.Scatter(x=t["Año"], 
                             y=t["Compromiso"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Compromiso',
                             fillcolor="#F7B261"))
    fig_line.add_trace(go.Scatter(x=t["Año"], 
                             y=t["Obligación"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Obligación',
                             fillcolor="#009999"))
    fig_line.add_trace(go.Scatter(x=t["Año"], 
                             y=t["Pago"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Pago',
                             fillcolor="#81D3CD"))

    # Customize layout
    fig_line.update_layout(
        title="Ejecución histórica",
        xaxis_title="Año",
        yaxis_title="Valor",
        template="plotly_white")
    for trace in fig_line.data:
        fig.add_trace(trace, row=1, col=1)

    for trace in fig_area.data:
        fig.add_trace(trace, row=1, col=2)

    fig.update_layout(showlegend=False, 
        hovermode='x unified')

    
    st.plotly_chart(fig)

    st.subheader("Sector")

    sector = st.selectbox("Seleccione el sector:", l_sectores)
    fil = ejec[ejec['Sector'] == sector]
    t = fil.pivot_table(index='Año',
                        columns='Etapa',
                        values='Valor_pc',
                        aggfunc='sum')
    tab = t.div(t['Apropiación'], axis=0).mul(100).round(1).reset_index()
    t = t.reset_index()
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Ejecución", "%"))
    
    fig_area = go.Figure()

    # Add traces
    fig_area.add_trace(go.Scatter(x=tab["Año"], 
                             y=tab["Apropiación"], 
                             fill='tozeroy',
                             mode='none', 
                             name='Apropiación',
                             fillcolor="#2635bf")
                             )
    fig_area.add_trace(go.Scatter(x=tab["Año"], 
                             y=tab["Compromiso"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Compromiso',
                             fillcolor="#F7B261"))
    fig_area.add_trace(go.Scatter(x=tab["Año"], 
                             y=tab["Obligación"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Obligación',
                             fillcolor="#009999"))
    fig_area.add_trace(go.Scatter(x=tab["Año"], 
                             y=tab["Pago"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Pago',
                             fillcolor="#81D3CD"))

    # Customize layout
    fig_area.update_layout(
        title="Ejecución histórica",
        xaxis_title="Año",
        yaxis_title="Valor",
        template="plotly_white")
    

    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(x=t["Año"], 
                             y=t["Apropiación"], 
                             fill='tozeroy',
                             mode='none', 
                             name='Apropiación',
                             fillcolor="#2635bf"))
    fig_line.add_trace(go.Scatter(x=t["Año"], 
                             y=t["Compromiso"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Compromiso',
                             fillcolor="#F7B261"))
    fig_line.add_trace(go.Scatter(x=t["Año"], 
                             y=t["Obligación"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Obligación',
                             fillcolor="#009999"))
    fig_line.add_trace(go.Scatter(x=t["Año"], 
                             y=t["Pago"], 
                             fill='tozeroy', 
                             mode='none', 
                             name='Pago',
                             fillcolor="#81D3CD"))

    # Customize layout
    fig_line.update_layout(
        title="Ejecución histórica",
        xaxis_title="Año",
        yaxis_title="Valor",
        template="plotly_white")
    for trace in fig_line.data:
        fig.add_trace(trace, row=1, col=1)

    for trace in fig_area.data:
        fig.add_trace(trace, row=1, col=2)

    fig.update_layout(showlegend=False, 
        hovermode='x unified')

    
    st.plotly_chart(fig)

elif selected_option == 'Recaudo histórico':

    tab1, tab2 = st.tabs(['General', 'Detallado'])

    with tab1:
        st.header("Recaudo histórico")

        a = rec.groupby(['Año'])['Valor_pc'].sum().reset_index()
        b = rec.pivot_table(index='Año',
                        columns='Rubro',
                        values='Valor_pc',
                        aggfunc='sum')
        c = b.div(b.sum(axis=1), axis=0).mul(100).round(1).stack().reset_index(name='%')


        fig_line = px.scatter(a, x='Año', y='Valor_pc', color_discrete_sequence=["#2635bf"])
        fig_line.update_traces(mode="lines+markers")

        fig_area1 = px.area(c, x='Año', y='%', color='Rubro',
                            color_discrete_sequence=["#2635bf", "#F7B261", "#81D3CD", "#009999"])
        fig_area2 = px.bar(pib_rec, x='Año', y='perc_total',
                            color_discrete_sequence=["#2635bf", "#F7B261", "#81D3CD", "#009999"])

        fig = make_subplots(rows=1, cols=3, subplot_titles=("Recaudo histórico", "% recaudo", "recaudo/PIB"), shared_xaxes=True)

        for trace in fig_line.data:
            fig.add_trace(trace, row=1, col=1)

        for trace in fig_area1.data:
            fig.add_trace(trace, row=1, col=2)

        for trace in fig_area2.data:
            fig.add_trace(trace, row=1, col=3)

        # Update layout
        fig.update_layout(height=400, width=1200, title_text="Recaudo histórico",
                        showlegend=False, hovermode='x unified')

        # Show figure
        st.plotly_chart(fig)

        st.subheader('Actividad interna')

        aint = rec[rec['Actividad'] == 'ACTIVIDAD INTERNA']
        a = aint.groupby(['Año'])['Valor_pc'].sum().reset_index()
        b = aint.pivot_table(index='Año',
                        columns='Rubro',
                        values='Valor_pc',
                        aggfunc='sum')
        c = b.div(b.sum(axis=1), axis=0).mul(100).round(1).stack().reset_index(name='%')


        fig_line = px.scatter(a, x='Año', y='Valor_pc', color_discrete_sequence=["#2635bf"])
        fig_line.update_traces(mode="lines+markers")

        fig_area1 = px.area(c, x='Año', y='%', color='Rubro',
                            color_discrete_sequence=["#2635bf", "#F7B261", "#81D3CD", "#009999"])
        fig_area2 = px.bar(pib_rec, x='Año', y='perc_interna',
                                color_discrete_sequence=["#2635bf", "#F7B261", "#81D3CD", "#009999"])

        fig = make_subplots(rows=1, cols=3, subplot_titles=("Recaudo histórico", "% recaudo", "recaudo/PIB"), shared_xaxes=True)

        for trace in fig_line.data:
            fig.add_trace(trace, row=1, col=1)

        for trace in fig_area1.data:
            fig.add_trace(trace, row=1, col=2)

        for trace in fig_area2.data:
            fig.add_trace(trace, row=1, col=3)

        # Update layout
        fig.update_layout(height=400, width=1200, title_text="Recaudo histórico",
                        showlegend=False, hovermode='x unified')
        
        st.plotly_chart(fig)


        st.subheader('Actividad externa')

        aext = rec[rec['Actividad'] == 'ACTIVIDAD EXTERNA']
        a = aext.groupby(['Año'])['Valor_pc'].sum().reset_index()
        b = aext.pivot_table(index='Año',
                        columns='Rubro',
                        values='Valor_pc',
                        aggfunc='sum')
        c = b.div(b.sum(axis=1), axis=0).mul(100).round(1).stack().reset_index(name='%')


        fig_line = px.scatter(a, x='Año', y='Valor_pc', color_discrete_sequence=["#2635bf"])
        fig_line.update_traces(mode="lines+markers")

        fig_area1 = px.area(c, x='Año', y='%', color='Rubro',
                            color_discrete_sequence=["#2635bf", "#F7B261", "#81D3CD", "#009999"])
        fig_area2 = px.bar(pib_rec, x='Año', y='perc_externa',
                                color_discrete_sequence=["#2635bf", "#F7B261", "#81D3CD", "#009999"])

        fig = make_subplots(rows=1, cols=3, subplot_titles=("Recaudo histórico", "% recaudo", "recaudo/PIB"), shared_xaxes=True)

        for trace in fig_line.data:
            fig.add_trace(trace, row=1, col=1)

        for trace in fig_area1.data:
            fig.add_trace(trace, row=1, col=2)

        for trace in fig_area2.data:
            fig.add_trace(trace, row=1, col=3)

        # Update layout
        fig.update_layout(height=400, width=1200, title_text="Recaudo histórico",
                        showlegend=False, hovermode='x unified')
        
        st.plotly_chart(fig)

    with tab2:
        st.header('Recaudo histórico')
        impuestos = pib_rec2['C2'].unique().tolist()
        tax = st.selectbox("Seleccione un impuesto: ", impuestos)
        fil = pib_rec2[pib_rec2['C2'] == tax]
        fil['Valor_pc'] /= 1_000_000

        fig_line = px.scatter(fil, x='Año', y='Valor_pc', color_discrete_sequence=["#2635bf"])
        fig_line.update_traces(mode="lines+markers")
        fig_area2 = px.bar(fil, x='Año', y='perc_pib',
                                color_discrete_sequence=["#2635bf", "#F7B261", "#81D3CD", "#009999"])

        fig = make_subplots(rows=1, cols=2, subplot_titles=("Recaudo histórico", "recaudo/PIB (%)"), shared_xaxes=True)

        for trace in fig_line.data:
            fig.add_trace(trace, row=1, col=1)

        for trace in fig_area2.data:
            fig.add_trace(trace, row=1, col=2)

        # Update layout
        fig.update_layout(height=400, width=1200, title_text="Recaudo histórico",
                        showlegend=False, hovermode='x unified')
        
        st.plotly_chart(fig)


elif selected_option == "PGN - 2025":
    
    st.header("PGN - 2025")
    
    pgn_25['TOTAL_mil'] = (pgn_25['TOTAL'] / 1_000_000).round(1)

    fig = px.treemap(pgn_25, path=[px.Constant('PGN'), 'Sector', 'Entidad', 'Tipo de gasto', 'CTA PROG','SUBC SUBP','OBJG PROY', 'ORD\nSPRY'],
                            values='TOTAL_mil',
                            title="Matriz de composición del presupuesto de 2025 <br><sup>Cifras en millones de pesos</sup>",
                            color_continuous_scale='Teal')

    fig.update_layout(width=1000, height=600)
            
    st.plotly_chart(fig)
    
    st.subheader("Descarga de datos")
    
    binary_output = BytesIO()
    pgn_25.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar datos de decreto',
                    data = binary_output.getvalue(),
                    file_name = 'pgn_2025.xlsx')    
    

    st.header("Decreto de aplazamiento - 2025")
    df2025['TOTAL_mil'] = (df2025['TOTAL'] / 1_000_000).round(1)

    fig = px.treemap(df2025, path=[px.Constant('Decreto'), 'Sector', 'Entidad', 'Tipo de gasto', 'CTA\nPROG', 'SUBC\nSUBP', 'OBJG\nPROY', 'ORD\nSPRY'],
                            values='TOTAL_mil',
                            title="Matriz de composición del decreto de aplazamiento <br><sup>Cifras en millones de pesos</sup>",
                            color_continuous_scale='Teal')

    fig.update_layout(width=1000, height=600)
            
    st.plotly_chart(fig)
    
    st.subheader("Visualización diferenciada")
    
    entidad = st.selectbox("Seleccione una entidad", diff['Entidad'].unique().tolist())
    
    diff_entidad = diff[diff['Entidad'] == entidad]
    
    st.dataframe(diff_entidad[['OBJG\nPROY','pgn_25','dec_aplaz', '% aplazado']].sort_values(by='% aplazado', ascending=False).reset_index(drop=True))

    st.subheader("Descarga de datos")


    binary_output = BytesIO()
    df2025.to_excel(binary_output, index=False)
    st.download_button(label = 'Descargar datos de decreto',
                    data = binary_output.getvalue(),
                    file_name = 'decreto_2025.xlsx')  

    

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
    with open('dictios/dictio.json', 'rb') as js:
        dictio = json.load(js)

    json_string = json.dumps(dictio)
    st.json(json_string, expanded=False)

    st.download_button(
        label='Descargar JSON',
        file_name='dictio.json',
        mime="application/json",
        data=json_string
    )





   
