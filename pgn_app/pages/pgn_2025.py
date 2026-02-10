import streamlit as st
import plotly.express as px
from io import BytesIO

def render(data, meta):
    pgn_25 = data["pgn_25"].copy()
    decreto = data["decreto_25"].copy()

    st.header("PGN - 2025")

    pgn_25["TOTAL_mil"] = (pgn_25["TOTAL"] / 1_000_000).round(1)
    fig = px.treemap(
        pgn_25,
        path=[px.Constant("PGN"), "Sector", "Entidad", "Tipo de gasto", "CTA PROG", "SUBC SUBP", "OBJG PROY", "ORD\nSPRY"],
        values="TOTAL_mil",
        title="Matriz de composición del presupuesto de 2025 <br><sup>Cifras en millones de pesos</sup>",
        color_continuous_scale="Teal",
    )
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Descarga de datos (PGN 2025)")
    bio = BytesIO()
    pgn_25.to_excel(bio, index=False)
    st.download_button("Descargar datos (pgn_2025.xlsx)", data=bio.getvalue(), file_name="pgn_2025.xlsx")

    st.divider()
    st.header("Decreto de aplazamiento - 2025")

    decreto["TOTAL_mil"] = (decreto["TOTAL"] / 1_000_000).round(1)
    fig = px.treemap(
        decreto,
        path=[px.Constant("Decreto"), "Sector", "Entidad", "Tipo de gasto", "CTA\nPROG", "SUBC\nSUBP", "OBJG\nPROY", "ORD\nSPRY"],
        values="TOTAL_mil",
        title="Matriz de composición del decreto de aplazamiento <br><sup>Cifras en millones de pesos</sup>",
        color_continuous_scale="Teal",
    )
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Descarga de datos (Decreto 2025)")
    bio = BytesIO()
    decreto.to_excel(bio, index=False)
    st.download_button("Descargar datos (decreto_2025.xlsx)", data=bio.getvalue(), file_name="decreto_2025.xlsx")
