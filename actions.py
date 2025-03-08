# --- Início de actions.py ---
import streamlit as st

DEFAULT_ACTIONS_CONFIG = {
    "placeholder_text": "Escreva algo",
    "opcoes": [
        "",
        "clicar_centro",
        "duplo_clique_centro",
        "clicar_botao_direito",
        "mover_mouse_para_centro",
        "captura_salva_area",
        "captura_tela_completa",
        "atalho_hotkey",
        "pressionar_teclas_basicas",
        "escrever_texto",
        "voltar_para_etapa",
        "pular_para_etapa",
        "inserir_item_lista"
    ],
    "atalho_options": ["", "ctrl+v", "ctrl+c", "shift+left", "shift+right"],
    "teclas_basicas_options": ["", "enter", "esc", "left", "right"]
}

def render_action_line(action_index, config=DEFAULT_ACTIONS_CONFIG, key_prefix=""):
    """
    Renderiza uma linha de ação usando um índice sequencial para compor as chaves.
    Exemplo de chave: "group1_acao1_select"
    """
    opcoes = config.get("opcoes", [])
    placeholder = config.get("placeholder_text", "Escreva algo")
    atalho_options = config.get("atalho_options", [])
    teclas_options = config.get("teclas_basicas_options", [])

    # Chave para o select da ação, ex: "group1_acao1_select"
    key_select = f"{key_prefix}_acao{action_index}_select"
    if key_select not in st.session_state:
        st.session_state[key_select] = opcoes[0]

    acao = st.selectbox(
        f"Ação {action_index}",
        opcoes,
        index=opcoes.index(st.session_state[key_select]),
        key=key_select
    )

    # Dependendo da ação selecionada, renderiza campos extras com chaves contextuais
    if acao in ["escrever_texto", "inserir_item_lista"]:
        key_text = f"{key_prefix}_acao{action_index}_texto"
        if key_text not in st.session_state:
            st.session_state[key_text] = ""
        st.text_input(
            "Texto",
            value=st.session_state[key_text],
            placeholder=placeholder,
            key=key_text
        )
    elif acao == "atalho_hotkey":
        key_atalho = f"{key_prefix}_acao{action_index}_atalho"
        if key_atalho not in st.session_state:
            st.session_state[key_atalho] = atalho_options[0]
        st.selectbox(
            "Atalho",
            atalho_options,
            index=atalho_options.index(st.session_state[key_atalho]),
            key=key_atalho
        )
    elif acao == "pressionar_teclas_basicas":
        key_tecla = f"{key_prefix}_acao{action_index}_tecla"
        if key_tecla not in st.session_state:
            st.session_state[key_tecla] = teclas_options[0]
        st.selectbox(
            "Tecla",
            teclas_options,
            index=teclas_options.index(st.session_state[key_tecla]),
            key=key_tecla
        )

    return acao

def render_actions_area(config=DEFAULT_ACTIONS_CONFIG, key_prefix=""):
    """
    Renderiza a área de ações de um grupo usando índices contextuais.
    Cada ação é identificada de forma sequencial (ex.: acao1, acao2, ...).
    """
    st.markdown("### Sequência de Ações")

    # Inicializa ou obtém a lista de índices das ações, ex: [1, 2]
    actions_key = f"{key_prefix}_acoes_list"
    if actions_key not in st.session_state:
        st.session_state[actions_key] = [1]  # inicia com a ação 1

    acoes = []
    for action_index in st.session_state[actions_key]:
        acao = render_action_line(action_index, config, key_prefix)
        acoes.append(acao)

    # Botões para adicionar ou remover ações usando chaves contextuais
    col_plus, col_trash = st.columns([0.1, 1])
    with col_plus:
        if st.button("➕", key=f"{key_prefix}_add_action"):
            # Gera o próximo índice sequencial (ex.: se [1,2] então novo será 3)
            novo_indice = max(st.session_state[actions_key]) + 1 if st.session_state[actions_key] else 1
            st.session_state[actions_key].append(novo_indice)
            st.rerun()
    with col_trash:
        if st.button("🗑️", key=f"{key_prefix}_remove_action"):
            if len(st.session_state[actions_key]) > 1:
                removed_index = st.session_state[actions_key].pop()
                # Limpa todas as chaves referentes à ação removida
                for key in list(st.session_state.keys()):
                    if key.startswith(f"{key_prefix}_acao{removed_index}_"):
                        del st.session_state[key]
                st.rerun()
            else:
                st.warning("Pelo menos uma linha de ação é necessária.")

    return acoes

# --- Fim de actions.py ---
