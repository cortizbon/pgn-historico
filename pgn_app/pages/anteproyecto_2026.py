import streamlit as st
import plotly.express as px
from datetime import datetime

current_year = datetime.now().year

def render(data, meta):
    # df26 = data["anteproyecto_26"].copy()

    # st.header("Anteproyecto 2026")

    # # Tu columna tiene un espacio: "Anteproyecto "
    # col = "Anteproyecto " if "Anteproyecto " in df26.columns else None
    # if col is None:
    #     st.error("No encuentro la columna 'Anteproyecto ' en el dataset.")
    #     st.stop()

    # df26["TOTAL_mil"] = (df26[col] / 1_000_000).round(1)

    # fig = px.treemap(
    #     df26,
    #     path=[px.Constant("PGN"), "Nombre Sector", "Entidad", "Tipo de gasto", "Cuenta", "Subcuenta", "Objeto", "Ordinal"],
    #     values="TOTAL_mil",
    #     title="Matriz de composición del anteproyecto en 2026 <br><sup>Cifras en millones de pesos</sup>",
    #     color_continuous_scale="Teal",
    # )
    # fig.update_layout(width=1000, height=600)
    # st.plotly_chart(fig, use_container_width=True)

    st.write(f"El anteproyecto de presupuesto para {current_year + 1} aún no está disponible. Por favor, vuelva más tarde para consultar esta información.")
