from __future__ import annotations

import pandas as pd
import streamlit as st
from pgn_app.paths import DATA_APP_DIR

def _read_csv(path) -> pd.DataFrame:
    return pd.read_csv(path)

def _read_xlsx(path) -> pd.DataFrame:
    # openpyxl viene por defecto en muchos entornos, pero asegúrate en requirements.txt
    return pd.read_excel(path)

@st.cache_data(show_spinner="Cargando datasets...")
def load_all() -> dict[str, pd.DataFrame]:
    # --- Core (los 4 “sí o sí”) ---
    gastos = _read_csv(DATA_APP_DIR / "gastos_def_2025_test.csv")
    ingresos = _read_csv(DATA_APP_DIR / "ingresos_2025.csv")
    ejecucion = _read_csv(DATA_APP_DIR / "ejecucion_hist.csv")
    recaudo = _read_csv(DATA_APP_DIR / "recaudo_hist.csv")

    # --- Otros que tu app actual usa ---
    pgn_25 = _read_csv(DATA_APP_DIR / "pgn_2025.csv")
    decreto_25 = _read_xlsx(DATA_APP_DIR / "decreto_2025.xlsx")
    diff = _read_xlsx(DATA_APP_DIR / "merge_william.xlsx")
    pib_rec = _read_csv(DATA_APP_DIR / "pib_rec.csv")
    pib_rec2 = _read_csv(DATA_APP_DIR / "c2_pib_rec.csv")
    anteproyecto_26 = _read_xlsx(DATA_APP_DIR / "datos_anteproyecto26.xlsx")
    pgn_pib = _read_csv(DATA_APP_DIR / "pgn_pib_2024.csv")
    pib_nominal = _read_csv(DATA_APP_DIR / "pib_nominal_24.csv")

    # --- Normalizaciones/compatibilidad (evita bugs por columnas inconsistentes) ---
    ingresos = ingresos.copy()
    if "Valor_25" in ingresos.columns and "Valor_25_esc" not in ingresos.columns:
        ingresos["Valor_25_esc"] = (ingresos["Valor_25"] / 1_000_000_000).round(1)

    gastos = gastos.copy()
    # Tus columnas originales (según el código pegado)
    if "Apropiación a precios corrientes" in gastos.columns:
        gastos["Apropiación a precios corrientes"] = gastos["Apropiación a precios corrientes"] / 1_000_000_000
    if "Apropiación a precios constantes (2025)" in gastos.columns:
        gastos["Apropiación a precios constantes (2025)"] = gastos["Apropiación a precios constantes (2025)"] / 1_000_000_000

    # En tu código mezclas "apropiacion_corrientes" con "Apropiación a precios corrientes"
    if "apropiacion_corrientes" not in gastos.columns and "Apropiación a precios corrientes" in gastos.columns:
        gastos["apropiacion_corrientes"] = gastos["Apropiación a precios corrientes"]

    return {
        "gastos": gastos,
        "ingresos": ingresos,
        "ejecucion": ejecucion,
        "recaudo": recaudo,
        "pgn_25": pgn_25,
        "decreto_25": decreto_25,
        "diff": diff,
        "pib_rec": pib_rec,
        "pib_rec2": pib_rec2,
        "anteproyecto_26": anteproyecto_26,
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
