import streamlit as st
import plotly.express as px
from utils import get_dic_colors, DIC_COLORES

def render(data, meta):
    df = data["gastos"].copy()
    inc = data["ingresos"].copy()

    st.header("Treemap")

    tab1, tab2 = st.tabs(["Ingreso", "Gasto"])

    with tab1:
        years_inc = sorted(inc["Año"].dropna().unique().astype(int).tolist())
        year = st.slider("Seleccione el año (ingreso)", min_value=min(years_inc), max_value=max(years_inc))

        fil = inc[inc["Año"] == year]
        fig = px.treemap(
            fil,
            path=[px.Constant("PGN"), "Ingreso", "Ingreso específico"],
            values="Valor_25_esc",
            color_discrete_sequence=[DIC_COLORES["ax_viol"][1], DIC_COLORES["ro_am_na"][3], DIC_COLORES["az_verd"][2]],
            title="Matriz de composición anual de ingreso del PGN <br><sup>Cifras en miles de millones de pesos</sup>",
        )
        fig.update_layout(width=1000, height=600)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        years_g = sorted(df["Año"].dropna().unique().astype(int).tolist())
        year = st.slider("Seleccione el año (gasto)", min_value=min(years_g), max_value=max(years_g))

        fil = df[df["Año"] == year]
        dic = get_dic_colors(fil)
        dic["(?)"] = "#D9D9ED"

        fig = px.treemap(
            fil,
            path=[px.Constant("PGN"), "Sector", "Entidad", "Tipo de gasto"],
            values="Apropiación a precios constantes (2025)",
            color="Sector",
            color_discrete_map=dic,
            title="Matriz de composición anual de gasto del PGN <br><sup>Cifras en miles de millones de pesos</sup>",
        )
        fig.update_layout(width=1000, height=600)
        st.plotly_chart(fig, use_container_width=True)
