import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

from utils import DIC_COLORES  # lo dejas en root para no romper notebooks

def render(data, meta):
    inc = data["ingresos"].copy()

    st.header("Ingresos")


    piv_year = inc.groupby("Año")["Valor a precios constantes (2026)"].sum().reset_index()
    fig = make_subplots(rows=1, cols=2, x_title="Año")

    fig.add_trace(
            go.Line(
                x=piv_year["Año"],
                y=piv_year["Valor a precios constantes (2026)"],
                name="Ingreso",
                line=dict(color=DIC_COLORES["ax_viol"][1]),
            ),
            row=1,
            col=1,
        )

    piv_tipo = (
            inc.groupby(["Año", "Ingreso_alt"])["Valor a precios constantes (2026)"]
            .sum()
            .reset_index()
        )
    piv_tipo["total"] = piv_tipo.groupby("Año")["Valor a precios constantes (2026)"].transform("sum")
    piv_tipo["%"] = ((piv_tipo["Valor a precios constantes (2026)"] / piv_tipo["total"]) * 100).round(2)

    val = 0.2
    for idx, (name, group) in enumerate(piv_tipo.groupby("Ingreso_alt")):
            fig.add_trace(
                go.Bar(
                    x=group["Año"],
                    y=group["%"],
                    name=name,
                    marker_color=DIC_COLORES["colors"][::-1][idx],
                    marker_pattern_size=6
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

    piv_year2 = inc.groupby(["Año", "Ingreso_alt"])["Valor a precios constantes (2026)"].sum().reset_index()
    fig2 = make_subplots(rows=1, cols=1, x_title="Año")
    
    for n, name in enumerate(piv_year2["Ingreso_alt"].unique()):
            fil = piv_year2[piv_year2["Ingreso_alt"] == name]
            fig2.add_trace(
                go.Line(
                    x=fil["Año"],
                    y=fil["Valor a precios constantes (2026)"],
                    name=name,
                    line=dict(color=DIC_COLORES["colors"][::-1][n]),
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

