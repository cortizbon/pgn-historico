import streamlit as st
import plotly.express as px
from io import BytesIO
from datetime import datetime
from utils import get_dic_colors

# extraer el año utilizando datetime para evitar hardcodear el año en el código
current_year = datetime.now().year

def render(data, meta):
    pgn_26 = data["pgn_26"].copy()

    st.header(f"PGN - {current_year}")

    pgn_26["TOTAL_mil"] = (pgn_26["Total"] / 1_000_000).round(1)
    dic = get_dic_colors(pgn_26, pgn_current=True)
    dic["(?)"] = "#D9D9ED"
    fig = px.treemap(
        pgn_26,
        path=[px.Constant("PGN"), "Sector", "Entidad", "Tipo de gasto", "Cuenta", "Subcuenta", "Proyecto", "Subproyecto"],
        values="TOTAL_mil",
        title="Matriz de composición del presupuesto de 2026 <br><sup>Cifras en millones de pesos</sup>",
        color="Sector",
        color_discrete_map=dic,
    )
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Descarga de datos (PGN {current_year})")
    bio = BytesIO()
    pgn_26.to_excel(bio, index=False)
    st.download_button("Descargar datos excel", data=bio.getvalue(), file_name=f"pgn_{current_year}.xlsx")