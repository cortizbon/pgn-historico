from streamlit_option_menu import option_menu

OPTIONS = [
    "Main",
    "Ingresos",
    "Gastos",
    "Treemap",
    "Ejecución histórica",
    "Recaudo histórico",
    "PGN - 2025",
    "Anteproyecto - 2026",
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
