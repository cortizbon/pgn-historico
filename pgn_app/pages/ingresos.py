import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

from utils import DIC_COLORES  # lo dejas en root para no romper notebooks

def render(data, meta):
    inc = data["ingresos"].copy()

    st.header("Ingresos")
    tab1, tab2, tab3 = st.tabs(["General", "Por sector", "Por entidad"])

    with tab1:
        piv_year = inc.groupby("Año")["Valor_25_esc"].sum().reset_index()
        fig = make_subplots(rows=1, cols=2, x_title="Año")

        fig.add_trace(
            go.Line(
                x=piv_year["Año"],
                y=piv_year["Valor_25_esc"],
                name="Ingreso",
                line=dict(color=DIC_COLORES["ax_viol"][1]),
            ),
            row=1,
            col=1,
        )

        piv_tipo = (
            inc.groupby(["Año", "Ingreso_alt"])["Valor_25_esc"]
            .sum()
            .reset_index()
        )
        piv_tipo["total"] = piv_tipo.groupby("Año")["Valor_25_esc"].transform("sum")
        piv_tipo["%"] = ((piv_tipo["Valor_25_esc"] / piv_tipo["total"]) * 100).round(2)

        val = 0.2
        for idx, (name, group) in enumerate(piv_tipo.groupby("Ingreso_alt")):
            fig.add_trace(
                go.Bar(
                    x=group["Año"],
                    y=group["%"],
                    name=name,
                    marker_color=DIC_COLORES["ro_am_na"][-idx + 1],
                    marker_pattern_size=6,
                    opacity=val,
                ),
                row=1,
                col=2,
            )
            val = min(val + 0.2, 1.0)

        fig.update_layout(
            barmode="stack",
            hovermode="x unified",
            width=1000,
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=-0.34, xanchor="right", x=1),
            title="Histórico general <br><sup>Cifras en miles de millones de pesos</sup>",
            yaxis_tickformat=".0f",
        )
        st.plotly_chart(fig, use_container_width=True)

        piv_year2 = inc.groupby(["Año", "Ingreso_alt"])["Valor_25_esc"].sum().reset_index()
        fig2 = make_subplots(rows=1, cols=1, x_title="Año")
        for n, name in enumerate(piv_year2["Ingreso_alt"].unique()):
            fil = piv_year2[piv_year2["Ingreso_alt"] == name]
            fig2.add_trace(
                go.Line(
                    x=fil["Año"],
                    y=fil["Valor_25_esc"],
                    name=name,
                    line=dict(color=DIC_COLORES["ro_am_na"][n]),
                ),
                row=1,
                col=1,
            )
        fig2.update_layout(
            hovermode="x unified",
            width=1000,
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=-0.34, xanchor="right", x=1),
            title="Histórico general <br><sup>Cifras en miles de millones de pesos</sup>",
            yaxis_tickformat=".0f",
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        d = inc[inc["Sector"] != "Nación"].copy()
        sectors = d["Sector"].dropna().unique().tolist()
        sector = st.selectbox("Seleccione un sector:", sectors, key="inc_sector")
        fil_sector = d[d["Sector"] == sector]
        piv_sec = fil_sector.groupby("Año")["Valor_25_esc"].sum().reset_index()

        fig = make_subplots(rows=1, cols=2, x_title="Año")
        fig.add_trace(
            go.Line(
                x=piv_sec["Año"],
                y=piv_sec["Valor_25_esc"],
                name="Ingreso total",
                line=dict(color=DIC_COLORES["ax_viol"][1]),
            ),
            row=1,
            col=1,
        )

        piv = (
            fil_sector.groupby(["Año", "Ingreso específico"])["Valor_25_esc"]
            .sum()
            .reset_index()
        )
        piv["total"] = piv.groupby("Año")["Valor_25_esc"].transform("sum")
        piv["%"] = ((piv["Valor_25_esc"] / piv["total"]) * 100).round(2)

        for name, group in piv.groupby("Ingreso específico"):
            fig.add_trace(go.Bar(x=group["Año"], y=group["%"], name=name), row=1, col=2)

        fig.update_layout(
            barmode="stack",
            hovermode="x unified",
            width=1000,
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=-0.34, xanchor="right", x=1),
            title="Histórico por sector <br><sup>Cifras en miles de millones de pesos</sup>",
            yaxis_tickformat=".0f",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        d = inc[inc["Sector"] != "Nación"].copy()
        sectors = d["Sector"].dropna().unique().tolist()
        sector = st.selectbox("Seleccione un sector:", sectors, key="inc_sector2")
        d = d[d["Sector"] == sector]
        ents = d["Entidad"].dropna().unique().tolist()
        ent = st.selectbox("Seleccione una entidad:", ents, key="inc_ent")
        fil_ent = d[d["Entidad"] == ent]
        piv_ent = fil_ent.groupby("Año")["Valor_25_esc"].sum().reset_index()

        fig = make_subplots(rows=1, cols=2, x_title="Año")
        fig.add_trace(
            go.Line(
                x=piv_ent["Año"],
                y=piv_ent["Valor_25_esc"],
                name="Ingreso",
                line=dict(color=DIC_COLORES["ax_viol"][1]),
            ),
            row=1,
            col=1,
        )

        piv = (
            fil_ent.groupby(["Año", "Ingreso específico"])["Valor_25_esc"]
            .sum()
            .reset_index()
        )
        piv["total"] = piv.groupby("Año")["Valor_25_esc"].transform("sum")
        piv["%"] = ((piv["Valor_25_esc"] / piv["total"]) * 100).round(2)

        for name, group in piv.groupby("Ingreso específico"):
            fig.add_trace(go.Bar(x=group["Año"], y=group["%"], name=name), row=1, col=2)

        fig.update_layout(
            barmode="stack",
            hovermode="x unified",
            width=1000,
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=-0.24, xanchor="right", x=1),
            title="Histórico por entidad <br><sup>Cifras en miles de millones de pesos</sup>",
            yaxis_tickformat=".0f",
        )
        st.plotly_chart(fig, use_container_width=True)
