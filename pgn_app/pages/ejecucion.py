import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def render(data, meta):
    ejec = data["ejecucion"].copy()

    st.header("Ejecución histórica (sin deuda)")

    # OJO: no mutar el DF cacheado “en vivo”
    ejec["Valor_pc"] = (ejec["Valor_pc"] / 1_000_000).round(1)

    l_sectores = sorted(ejec["Sector"].dropna().unique().tolist())

    def _plot_block(df_):
        t = df_.pivot_table(index="Año", columns="Etapa", values="Valor_pc", aggfunc="sum").reset_index()
        tab = df_.pivot_table(index="Año", columns="Etapa", values="Valor_pc", aggfunc="sum")
        tab_pct = tab.div(tab["Apropiación"], axis=0).mul(100).round(1).reset_index()

        fig = make_subplots(rows=1, cols=2, subplot_titles=("Ejecución", "%"))

        # “Valores”
        for etapa, fill in [("Apropiación", "#2635bf"), ("Compromiso", "#F7B261"), ("Obligación", "#009999"), ("Pago", "#81D3CD")]:
            if etapa in t.columns:
                fig.add_trace(go.Scatter(x=t["Año"], y=t[etapa], fill="tozeroy", mode="none", name=etapa, fillcolor=fill), row=1, col=1)

        # “Porcentajes”
        for etapa, fill in [("Apropiación", "#2635bf"), ("Compromiso", "#F7B261"), ("Obligación", "#009999"), ("Pago", "#81D3CD")]:
            if etapa in tab_pct.columns:
                fig.add_trace(go.Scatter(x=tab_pct["Año"], y=tab_pct[etapa], fill="tozeroy", mode="none", name=etapa, fillcolor=fill), row=1, col=2)

        fig.update_layout(showlegend=False, hovermode="x unified")
        return fig

    st.subheader("General")
    st.plotly_chart(_plot_block(ejec), use_container_width=True)

    st.subheader("Sector")
    sector = st.selectbox("Seleccione el sector:", l_sectores, key="ej_sector")
    fil = ejec[ejec["Sector"] == sector].copy()
    st.plotly_chart(_plot_block(fil), use_container_width=True)
