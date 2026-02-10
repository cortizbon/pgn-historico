import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots

def render(data, meta):
    rec = data["recaudo"].copy()
    pib_rec = data["pib_rec"].copy()
    pib_rec2 = data["pib_rec2"].copy()

    tab1, tab2 = st.tabs(["General", "Detallado"])

    with tab1:
        st.header("Recaudo histórico")

        a = rec.groupby(["Año"])["Valor_pc"].sum().reset_index()
        b = rec.pivot_table(index="Año", columns="Rubro", values="Valor_pc", aggfunc="sum")
        c = b.div(b.sum(axis=1), axis=0).mul(100).round(1).stack().reset_index(name="%")

        fig_line = px.scatter(a, x="Año", y="Valor_pc", color_discrete_sequence=["#2635bf"])
        fig_line.update_traces(mode="lines+markers")

        fig_area1 = px.area(c, x="Año", y="%", color="Rubro",
                            color_discrete_sequence=["#2635bf", "#F7B261", "#81D3CD", "#009999"])
        fig_area2 = px.bar(pib_rec, x="Año", y="perc_total", color_discrete_sequence=["#2635bf"])

        fig = make_subplots(rows=1, cols=3, subplot_titles=("Recaudo histórico", "% recaudo", "recaudo/PIB"), shared_xaxes=True)
        for tr in fig_line.data: fig.add_trace(tr, row=1, col=1)
        for tr in fig_area1.data: fig.add_trace(tr, row=1, col=2)
        for tr in fig_area2.data: fig.add_trace(tr, row=1, col=3)

        fig.update_layout(height=400, width=1200, title_text="Recaudo histórico", showlegend=False, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Recaudo histórico (detallado)")

        impuestos = sorted(pib_rec2["C2"].dropna().unique().tolist())
        tax = st.selectbox("Seleccione un impuesto:", impuestos, key="rec_tax")

        fil = pib_rec2[pib_rec2["C2"] == tax].copy()
        fil["Valor_pc"] = fil["Valor_pc"] / 1_000_000

        fig_line = px.scatter(fil, x="Año", y="Valor_pc", color_discrete_sequence=["#2635bf"])
        fig_line.update_traces(mode="lines+markers")
        fig_bar = px.bar(fil, x="Año", y="perc_pib", color_discrete_sequence=["#2635bf"])

        fig = make_subplots(rows=1, cols=2, subplot_titles=("Recaudo", "recaudo/PIB (%)"), shared_xaxes=True)
        for tr in fig_line.data: fig.add_trace(tr, row=1, col=1)
        for tr in fig_bar.data: fig.add_trace(tr, row=1, col=2)

        fig.update_layout(height=400, width=1200, showlegend=False, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
