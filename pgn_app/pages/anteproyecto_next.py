import streamlit as st
import plotly.express as px
from datetime import datetime
from utils import get_dic_colors

current_year = datetime.now().year

def render(data, meta):
    df27 = data["anteproyecto_27"].copy()
    p27 = data["proyecto_27"].copy()

    st.header("Anteproyecto 2027")

    df27["TOTAL_mil"] = (df27['Total'] / 1_000_000).round(1)
    dic = get_dic_colors(df27, pgn_current=True)
    dic["(?)"] = "#D9D9ED"
    fig = px.treemap(
        df27,
        path=[px.Constant("PGN"), "Sector", "Entidad", "Tipo de gasto", "Cuenta", "Subcuenta", "Objeto", "Ordinal"],
        values="TOTAL_mil",
        title="Matriz de composición del anteproyecto en 2027 <br><sup>Cifras en millones de pesos</sup>",
        color='Sector',
        color_discrete_map=dic,
    )
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.header("Proyecto de Ley PGN - 2027")

    p27["TOTAL_mil"] = (p27['Total'] / 1_000_000).round(1)
    dic = get_dic_colors(p27, pgn_current=True)
    dic["(?)"] = "#D9D9ED"
    fig = px.treemap(
        df27,
        path=[px.Constant("PGN"), "Sector", "Entidad", "Tipo de gasto"],
        values="TOTAL_mil",
        title="Matriz de composición del anteproyecto en 2027 <br><sup>Cifras en millones de pesos</sup>",
        color='Sector',
        color_discrete_map=dic,
    )
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig, use_container_width=True)   

    #st.write(f"El anteproyecto de presupuesto para {current_year + 1} aún no está disponible. Estamos a la espera de una actualización del Ministerio de Hacienda y Crédito Público.")
