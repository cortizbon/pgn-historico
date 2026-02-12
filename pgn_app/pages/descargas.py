import streamlit as st
import json
from io import BytesIO
from pathlib import Path

from utils import convert_df  # tu helper
from pgn_app.paths import DICTS_DIR

def render(data, meta):
    df = data["gastos"].copy()
    st.header("Descarga de datos")

    st.subheader("Descarga de dataset completo")
    bio = BytesIO()
    df.to_excel(bio, index=False)
    st.download_button("Descargar datos completos (xlsx)", data=bio.getvalue(), file_name="gastos_completo.xlsx")

    st.divider()
    st.subheader("Descarga de dataset filtrado")

    col1, col2 = st.columns(2)

    with col1:
        sectors = sorted(df["Sector"].dropna().unique().tolist())
        entities = sorted(df["Entidad"].dropna().unique().tolist())
        years = sorted(df["Año"].dropna().unique().astype(int).tolist())

        sectors_2 = ["Todos"] + sectors
        sectors_selected = st.multiselect("Sector(es)", sectors_2)
        if "Todos" in sectors_selected or not sectors_selected:
            filter_ss = df[df["Sector"].isin(sectors)]
        else:
            filter_ss = df[df["Sector"].isin(sectors_selected)]

        entities_2 = ["Todas"] + sorted(filter_ss["Entidad"].dropna().unique().tolist())
        entities_selected = st.multiselect("Entidad(es)", entities_2)
        if "Todas" in entities_selected or not entities_selected:
            entities_selected = sorted(filter_ss["Entidad"].dropna().unique().tolist())

        years_2 = ["Todos"] + years
        years_selected = st.multiselect("Año(s)", years_2)
        if "Todos" in years_selected or not years_selected:
            years_selected = years

        filter_s_e_y = filter_ss[
            (filter_ss["Entidad"].isin(entities_selected)) &
            (filter_ss["Año"].isin(years_selected))
        ]

    with col2:
        prices = {
            "corrientes": "Apropiación a precios corrientes",
            "constantes 2026": "Apropiación a precios constantes (2026)",
        }
        price_selected = st.selectbox("Nivel(es) de precios", list(prices.keys()))
        total_or_account = st.selectbox("Suma o por cuenta", ["suma", "por cuenta"])

        if total_or_account == "suma":
            pivot = (
                filter_s_e_y.groupby(["Año", "Sector", "Entidad"])[prices[price_selected]]
                .sum()
                .reset_index()
            )
        else:
            pivot = (
                filter_s_e_y.groupby(["Año", "Sector", "Entidad", "Tipo de gasto"])[prices[price_selected]]
                .sum()
                .reset_index()
            )

        show = st.button("Vista previa")

    if show:
        st.dataframe(pivot)
        csv = convert_df(pivot)
        st.download_button("Descargar CSV", data=csv, file_name="datos_filtrados.csv", mime="text/csv")

        bio = BytesIO()
        pivot.to_excel(bio, index=False)
        st.download_button("Descargar Excel", data=bio.getvalue(), file_name="datos_filtrados.xlsx")

    st.divider()
    st.subheader("Descarga del árbol sector-entidad del PGN")

    # Arregla el bug: tú tienes dicts/, no dictios/
    candidates = [
        DICTS_DIR / "dictio.json",
        Path("dictios") / "dictio.json",
    ]
    path = next((p for p in candidates if p.exists()), None)
    if path is None:
        st.warning("No encontré dictio.json en dicts/ (ni en dictios/).")
        return

    with open(path, "rb") as f:
        dictio = json.load(f)

    json_string = json.dumps(dictio, ensure_ascii=False)
    st.json(json_string, expanded=False)

    st.download_button(
        "Descargar JSON",
        file_name="dictio.json",
        mime="application/json",
        data=json_string,
    )
