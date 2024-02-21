import streamlit as st
from streamlit_option_menu import option_menu

with st.sidebar:
    selected_option = option_menu("Menú", ["Main", "Histórico general", "Histórico por sector", "Histórico por entidad", "Treemap", "Descarga de datos"], 
        icons=['arrow-right-short', 'file-bar-graph', 'intersect', "list-task", 'columns', 'cloud-download'], 
        menu_icon="p", default_index=0, orientation="vertical")
    
if selected_option == "Histórico general":
    st.write(selected_option)

