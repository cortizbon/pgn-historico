from streamlit_option_menu import option_menu
from datetime import datetime

current_year = datetime.now().year

OPTIONS = [
    "Main",
    "Ingresos",
    "Gastos",
    "Treemap",
    "Ejecución histórica",
    "Recaudo histórico",
    f"PGN - {current_year}",
    f"Anteproyecto - {current_year + 1}",
    "Descarga de datos",
]

ICONS = [
    "arrow-right-short",
    "file-bar-graph",
    "intersect",
    "columns",
    "cart2",
    "bag",
    "building-fill",
    "building-fill",
    "cloud-download",
]

def render_nav() -> str:
    return option_menu(
        None,
        OPTIONS,
        icons=ICONS,
        menu_icon="p",
        default_index=0,
        orientation="horizontal",
    )
