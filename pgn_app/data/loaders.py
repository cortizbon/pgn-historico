from __future__ import annotations

import pandas as pd
import streamlit as st
from pgn_app.paths import DATA_APP_DIR

def _read_csv(path) -> pd.DataFrame:
    return pd.read_csv(path)

def _read_xlsx(path) -> pd.DataFrame:
    
    return pd.read_excel(path)

def _read_parquet(path) -> pd.DataFrame:
    return pd.read_parquet(path)

@st.cache_data(show_spinner="Cargando datasets...")
def load_all() -> dict[str, pd.DataFrame]:
    
    gastos = _read_csv(DATA_APP_DIR / "gastos_def_2026.csv")
    ingresos = _read_csv(DATA_APP_DIR / "ingresos_2026.csv")
    ejecucion = _read_csv(DATA_APP_DIR / "ejecucion_hist.csv")
    recaudo = _read_csv(DATA_APP_DIR / "recaudo_hist.csv")

    
    pgn_26 = _read_csv(DATA_APP_DIR / "desag_2026.csv")
    decreto_25 = _read_xlsx(DATA_APP_DIR / "decreto_2025.xlsx")
    diff = _read_xlsx(DATA_APP_DIR / "merge_william.xlsx")
    pib_rec = _read_csv(DATA_APP_DIR / "pib_rec.csv")
    pib_rec2 = _read_csv(DATA_APP_DIR / "c2_pib_rec.csv")
    anteproyecto_27 = _read_parquet(DATA_APP_DIR / "datos_anteproyecto27.parquet")
    proyecto_27 = _read_csv(DATA_APP_DIR / "proyecto_pgn.csv")
    pgn_pib = _read_csv(DATA_APP_DIR / "pgn_pib_2024.csv")
    pib_nominal = _read_csv(DATA_APP_DIR / "pib_nominal_24.csv")

    
    ingresos = ingresos.copy()
    if  "Valor a precios constantes (2026)" in ingresos.columns:
        ingresos["Valor a precios constantes (2026)"] = (ingresos["Valor a precios constantes (2026)"] / 1_000_000_000).round(1)

    gastos = gastos.copy()
    
    if "Apropiación a precios corrientes" in gastos.columns:
        gastos["Apropiación a precios corrientes"] = gastos["Apropiación a precios corrientes"] / 1_000_000_000
    if "Apropiación a precios constantes (2026)" in gastos.columns:
        gastos["Apropiación a precios constantes (2026)"] = gastos["Apropiación a precios constantes (2026)"] / 1_000_000_000

    
    if "apropiacion_corrientes" not in gastos.columns and "Apropiación a precios corrientes" in gastos.columns:
        gastos["apropiacion_corrientes"] = gastos["Apropiación a precios corrientes"]

    return {
        "gastos": gastos,
        "ingresos": ingresos,
        "ejecucion": ejecucion,
        "recaudo": recaudo,
        "pgn_26": pgn_26,
        "decreto_25": decreto_25,
        "diff": diff,
        "pib_rec": pib_rec,
        "pib_rec2": pib_rec2,
        "anteproyecto_27": anteproyecto_27,
        "pgn_pib": pgn_pib,
        "pib_nominal": pib_nominal,
    }

def build_meta(data: dict[str, pd.DataFrame]) -> dict[str, list]:
    gastos = data["gastos"]
    ingresos = data["ingresos"]

    years = sorted(
        set(pd.to_numeric(gastos["Año"], errors="coerce").dropna().astype(int).tolist())
        | set(pd.to_numeric(ingresos["Año"], errors="coerce").dropna().astype(int).tolist())
    )

    sectors = sorted(gastos["Sector"].dropna().unique().tolist()) if "Sector" in gastos.columns else []
    entities = sorted(gastos["Entidad"].dropna().unique().tolist()) if "Entidad" in gastos.columns else []

    return {"years": years, "sectors": sectors, "entities": entities}
