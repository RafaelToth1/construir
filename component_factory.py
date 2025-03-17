# --- Início de component_factory.py ---
# component_factory.py
import streamlit as st
from upload import renderizarAreaUpload, CONFIG_UPLOAD_PADRAO
from actions import renderizarAreaAcoes, CONFIG_ACOES_PADRAO

COMPONENTES = {
    "upload": lambda prefixoChave: renderizarAreaUpload(CONFIG_UPLOAD_PADRAO, prefixoChave=prefixoChave),
    "actions": lambda prefixoChave: renderizarAreaAcoes(CONFIG_ACOES_PADRAO, prefixoChave=prefixoChave)
}

def criarComponente(tipoComponente: str, prefixoChave: str = "", **kwargs):
    func = COMPONENTES.get(tipoComponente)
    if func:
        return func(prefixoChave)
    st.error(f"Componente do tipo '{tipoComponente}' não é reconhecido.")
    return None
