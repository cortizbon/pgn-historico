from pgn_app.ui.layout import set_layout, header
from pgn_app.ui.navigation import render_nav
from pgn_app.data.loaders import load_all, build_meta

from pgn_app.pages import (
    main, ingresos, gastos, treemap, ejecucion, recaudo, pgn_2025, anteproyecto_2026, descargas
)
from datetime import datetime

current_year = datetime.now().year

ROUTES = {
    "Main": main,
    "Ingresos": ingresos,
    "Gastos": gastos,
    "Treemap": treemap,
    "Ejecución histórica": ejecucion,
    "Recaudo histórico": recaudo,
    f"PGN - {current_year}": pgn_2025,
    f"Anteproyecto - {current_year + 1}": anteproyecto_2026,
    "Descarga de datos": descargas,
}

def run():
    set_layout()
    header()

    data = load_all()
    meta = build_meta(data)

    choice = render_nav()
    page = ROUTES[choice]
    page.render(data, meta)

if __name__ == "__main__":
    run()
