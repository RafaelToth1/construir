# --- Início de component_factory.py ---
import streamlit as st
from upload import render_upload_area, DEFAULT_UPLOAD_CONFIG
from actions import render_actions_area, DEFAULT_ACTIONS_CONFIG

DEFAULT_GROUP_TEXT_CONFIG = {
    "placeholder": "Digite o nome do grupo",
}

def render_group_text(config: dict = DEFAULT_GROUP_TEXT_CONFIG, key_prefix: str = "", initial_value: str = "") -> str:
    placeholder = config.get("placeholder", "Digite o nome do grupo")
    key = f"{key_prefix}_group_text"
    if key not in st.session_state:
        st.session_state[key] = initial_value
    return st.text_input("Nome do Grupo", placeholder=placeholder, key=key)

def create_component(component_type: str, key_prefix: str = "", **kwargs):
    if component_type == "upload":
        return render_upload_area(DEFAULT_UPLOAD_CONFIG, key_prefix=key_prefix)
    elif component_type == "actions":
        return render_actions_area(DEFAULT_ACTIONS_CONFIG, key_prefix=key_prefix)
    elif component_type == "group_text":
        return render_group_text(DEFAULT_GROUP_TEXT_CONFIG, key_prefix=key_prefix, **kwargs)
    else:
        st.error(f"Componente do tipo '{component_type}' não é reconhecido.")
        return None

# --- Fim de component_factory.py ---
