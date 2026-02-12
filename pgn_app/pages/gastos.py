import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from utils import DIC_COLORES

def render(data, meta):
    df = data["gastos"].copy()
    pgn_pib = data["pgn_pib"].copy()

    st.header("Gastos")

    years = meta["years"]
    sectors = meta["sectors"]

    dict_gasto = {
        "Funcionamiento": DIC_COLORES["az_verd"][2],
        "Deuda": DIC_COLORES["ax_viol"][1],
        "Inversión": DIC_COLORES["ro_am_na"][3],
    }

    prices = {
        "corrientes": "Apropiación a precios corrientes",
        "constantes 2026": "Apropiación a precios constantes (2026)",
    }

    tab1, tab2, tab3 = st.tabs(["General", "Por sector", "Por entidad"])

    with tab1:
        piv = df.groupby("Año")["Apropiación a precios constantes (2026)"].sum().reset_index()

        # CAGR general (usa extremos 2013 vs 2026 como en tu lógica original)
        if (piv["Año"] == 2013).any() and (piv["Año"] == 2026).any():
            v0 = piv.loc[piv["Año"] == 2013, "Apropiación a precios constantes (2026)"].iloc[0]
            v1 = piv.loc[piv["Año"] == 2026, "Apropiación a precios constantes (2026)"].iloc[0]
            tasa_gen_cagr = (v1 / v0) ** (1 / (2026 - 2013)) - 1
        else:
            tasa_gen_cagr = 0.0

        fig = make_subplots(
            rows=1, cols=3, x_title="Año",
            subplot_titles=(
                "Apropiación a precios constantes (2026)",
                "Composición del gasto (en %)",
                "Gasto como % del PIB",
            ),
        )

        fig.add_trace(
            go.Line(
                x=piv["Año"],
                y=piv["Apropiación a precios constantes (2026)"],
                name="Constantes (2026)",
                line=dict(color=DIC_COLORES["ax_viol"][1]),
            ),
            row=1, col=1,
        )
        fig.update_yaxes(rangemode="tozero", row=1, col=1)

        piv_tipo = (
            df.groupby(["Año", "Tipo de gasto"])["Apropiación a precios constantes (2026)"]
            .sum()
            .reset_index()
        )
        piv_tipo["total"] = piv_tipo.groupby("Año")["Apropiación a precios constantes (2026)"].transform("sum")
        piv_tipo["%"] = ((piv_tipo["Apropiación a precios constantes (2026)"] / piv_tipo["total"]) * 100).round(2)

        for tipo, group in piv_tipo.groupby("Tipo de gasto"):
            fig.add_trace(
                go.Bar(
                    x=group["Año"],
                    y=group["%"],
                    name=tipo,
                    marker_color=dict_gasto.get(tipo, "#999999"),
                ),
                row=1, col=2,
            )

        # Barras gasto/PIB (ya viene armado)
        for col, color in [("Deuda", DIC_COLORES["ax_viol"][1]), ("Funcionamiento", DIC_COLORES["az_verd"][2]), ("Inversión", DIC_COLORES["ro_am_na"][3])]:
            if col in pgn_pib.columns:
                fig.add_trace(go.Bar(x=pgn_pib["Año"], y=pgn_pib[col], name=col, marker_color=color, showlegend=False), row=1, col=3)

        fig.update_layout(
            barmode="stack",
            hovermode="x unified",
            width=1200,
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=-0.34, xanchor="right", x=1),
            title="Histórico general <br><sup>Cifras en miles de millones de pesos</sup>",
            yaxis_tickformat=".0f",
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        sector = st.selectbox("Seleccione el sector", sectors, key="g_sector")
        fil = df[df["Sector"] == sector].copy()

        piv_sector = fil.pivot_table(index="Año", values=list(prices.values()), aggfunc="sum").reset_index()

        fig = make_subplots(rows=1, cols=2, x_title="Año", shared_yaxes=True)
        fig.add_trace(
            go.Line(
                x=piv_sector["Año"],
                y=piv_sector["Apropiación a precios constantes (2026)"],
                name="Constantes (2026)",
                line=dict(color=DIC_COLORES["ax_viol"][1]),
            ),
            row=1, col=1,
        )

        piv_tipo = (
            fil.groupby(["Año", "Tipo de gasto"])["Apropiación a precios constantes (2026)"]
            .sum()
            .reset_index()
        )
        for tipo, group in piv_tipo.groupby("Tipo de gasto"):
            fig.add_trace(go.Bar(x=group["Año"], y=group["Apropiación a precios constantes (2026)"], name=tipo, marker_color=dict_gasto.get(tipo, "#999999")), row=1, col=2)

        fig.update_layout(
            barmode="stack",
            hovermode="x unified",
            width=1000,
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=-0.34, xanchor="right", x=1),
            title=f"{sector} <br><sup>Cifras en miles de millones de pesos</sup>",
            yaxis_tickformat=".0f",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        sector = st.selectbox("Seleccione el sector", sectors, key="g_sector2")
        fil_sector = df[df["Sector"] == sector].copy()
        entities_sector = sorted(fil_sector["Entidad"].dropna().unique().tolist())
        entidad = st.selectbox("Seleccione la entidad", entities_sector, key="g_ent")

        fil = fil_sector[fil_sector["Entidad"] == entidad].copy()
        piv = fil.pivot_table(index="Año", values=list(prices.values()), aggfunc="sum").reset_index()

        fig = make_subplots(rows=1, cols=2, x_title="Año", shared_yaxes=True)
        fig.add_trace(
            go.Line(
                x=piv["Año"],
                y=piv["Apropiación a precios constantes (2026)"],
                name="Constantes (2026)",
                line=dict(color=DIC_COLORES["ax_viol"][1]),
            ),
            row=1, col=1,
        )

        piv_tipo = (
            fil.groupby(["Año", "Tipo de gasto"])["Apropiación a precios constantes (2026)"]
            .sum()
            .reset_index()
        )
        for tipo, group in piv_tipo.groupby("Tipo de gasto"):
            fig.add_trace(go.Bar(x=group["Año"], y=group["Apropiación a precios constantes (2026)"], name=tipo, marker_color=dict_gasto.get(tipo, "#999999")), row=1, col=2)

        fig.update_layout(
            barmode="stack",
            hovermode="x unified",
            width=1000,
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=-0.34, xanchor="right", x=1),
            title=f"{entidad} <br><sup>Cifras en miles de millones de pesos</sup>",
            yaxis_tickformat=".0f",
        )
        st.plotly_chart(fig, use_container_width=True)
