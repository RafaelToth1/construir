import streamlit as st
import logging
import uuid
from utils import get_action_key

CONFIG_ACOES_PADRAO = {
    "placeholder_text": "Escreva algo",
    "opcoes": ["", "aguardar", "avancar_item_lista", "clicar_centro", "duplo_clique_centro", "clicar_botao_direito", "mover_mouse_para_centro", "captura_salva_area", "captura_tela_completa", "atalho_hotkey", "pressionar_teclas_basicas", "escrever_texto", "voltar_para_etapa", "pular_para_etapa", "inserir_item_lista", "verificar_continuidade"],
    "atalho_options": ["", "ctrl+v", "ctrl+c", "ctrl+p", "shift+left", "shift+right"],
    "teclas_basicas_options": ["", "enter", "esc", "left", "right", "win"]
}

def renderizarLinhaAcao(acao_id, config, prefixoChave):
    chaveSelect = f"{prefixoChave}_acao{acao_id}_select"
    options = config.get("opcoes", [])
    if chaveSelect not in st.session_state or st.session_state[chaveSelect] not in options:
        st.session_state[chaveSelect] = options[0]
    acao = st.selectbox("Selecione a ação:", options, index=options.index(st.session_state[chaveSelect]), key=chaveSelect)
    return acao

def _render_text_input(prefixoChave, acao_id, suffix, label, placeholder, default=""):
    chave = f"{prefixoChave}_acao{acao_id}_{suffix}"
    if chave not in st.session_state:
        st.session_state[chave] = default
    st.text_input(label, value=st.session_state[chave], placeholder=placeholder, key=chave)

def _render_selectbox(prefixoChave, acao_id, suffix, label, options):
    chave = f"{prefixoChave}_acao{acao_id}_{suffix}"
    if chave not in st.session_state:
        st.session_state[chave] = options[0]
    st.selectbox(label, options, index=options.index(st.session_state[chave]), key=chave)

def _render_text_input_with_options(prefixoChave, acao_id, suffix, label, placeholder, default=""):
    formatos = st.session_state.get("formatos_solicitados", [])
    chave = f"{prefixoChave}_acao{acao_id}_{suffix}"
    if formatos:
        opcoes = formatos + ["Outro (Digite manualmente)"]
        if chave not in st.session_state:
            st.session_state[chave] = opcoes[0]
        escolha = st.selectbox(label, opcoes, index=opcoes.index(st.session_state[chave]), key=chave)
        if escolha == "Outro (Digite manualmente)":
            manual_key = f"{chave}_manual"
            if manual_key not in st.session_state:
                st.session_state[manual_key] = ""
            return st.text_input("Digite o valor", key=manual_key, placeholder=placeholder)
        else:
            return escolha
    else:
        _render_text_input(prefixoChave, acao_id, suffix, label, placeholder, default)

PARAM_WIDGETS = {
    "escrever_texto": lambda acao_id, prefixoChave: _render_text_input(prefixoChave, acao_id, "texto", "Texto", CONFIG_ACOES_PADRAO.get("placeholder_text", "Escreva algo")),
    "inserir_item_lista": lambda acao_id, prefixoChave: _render_text_input_with_options(prefixoChave, acao_id, "texto", "Texto", CONFIG_ACOES_PADRAO.get("placeholder_text", "Escreva algo")),
    "verificar_continuidade": lambda acao_id, prefixoChave: _render_text_input_with_options(prefixoChave, acao_id, "texto", "Texto", CONFIG_ACOES_PADRAO.get("placeholder_text", "Escreva algo")),
    "atalho_hotkey": lambda acao_id, prefixoChave: _render_selectbox(prefixoChave, acao_id, "atalho", "Atalho", CONFIG_ACOES_PADRAO.get("atalho_options", [])),
    "pressionar_teclas_basicas": lambda acao_id, prefixoChave: _render_selectbox(prefixoChave, acao_id, "tecla", "Tecla", CONFIG_ACOES_PADRAO.get("teclas_basicas_options", [])),
    "aguardar": lambda acao_id, prefixoChave: _render_text_input(prefixoChave, acao_id, "aguardar", "Tempo de espera (segundos)", "Insira um número (em segundos)", default="2")
}

def renderizarParametroAcao(acao, acao_id, config, prefixoChave):
    if acao in PARAM_WIDGETS:
        PARAM_WIDGETS[acao](acao_id, prefixoChave)
    else:
        st.empty()

def removerCampoAcao(acao_id, prefixoChave):
    prefixo = f"{prefixoChave}_acao{acao_id}_"
    keysToRemove = [key for key in st.session_state if key.startswith(prefixo)]
    for key in keysToRemove:
        del st.session_state[key]

def adicionarCampoAcao(listaAcoes, indice, prefixoChave):
    novoId = str(uuid.uuid4())
    novaLista = listaAcoes[:indice+1] + [novoId] + listaAcoes[indice+1:]
    st.session_state[f"{prefixoChave}_listaAcoes"] = novaLista
    st.rerun()

def renderizarAreaAcoes(config=CONFIG_ACOES_PADRAO, prefixoChave=""):
    st.markdown("### Sequência de Ações")
    chaveListaAcoes = f"{prefixoChave}_listaAcoes"
    if chaveListaAcoes not in st.session_state:
        st.session_state[chaveListaAcoes] = [str(uuid.uuid4())]
    listaAcoes = st.session_state[chaveListaAcoes]
    chaveReorder = f"{prefixoChave}_mostrar_reordenacao_acoes"
    with st.expander("Ações (Modo Normal)", expanded=not st.session_state.get(chaveReorder, False)):
        for i, acao_id in enumerate(listaAcoes):
            cols = st.columns([4, 4, 1, 1])
            with cols[0]:
                acao_selecionada = renderizarLinhaAcao(acao_id, config, prefixoChave)
            with cols[1]:
                if acao_selecionada in PARAM_WIDGETS:
                    renderizarParametroAcao(acao_selecionada, acao_id, config, prefixoChave)
                else:
                    st.empty()
            with cols[2]:
                if st.button("➕", key=f"{prefixoChave}_add_{acao_id}"):
                    adicionarCampoAcao(listaAcoes, i, prefixoChave)
            with cols[3]:
                if st.button("–", key=f"{prefixoChave}_remove_{acao_id}"):
                    if len(listaAcoes) > 1:
                        removerCampoAcao(acao_id, prefixoChave)
                        novaLista = [x for x in listaAcoes if x != acao_id]
                        st.session_state[chaveListaAcoes] = novaLista
                    else:
                        st.warning("Pelo menos uma linha de ação é necessária.")
        if not st.session_state.get(chaveReorder, False):
            if st.button("Reordenar Ações", key=f"{prefixoChave}_reorder_actions"):
                st.session_state[chaveReorder] = True
    if st.session_state.get(chaveReorder, False):
        with st.expander("Reordenar Ações", expanded=True):
            st.markdown("#### Reordenar Ações")
            for acao_id in listaAcoes:
                current_type = st.session_state.get(f"{prefixoChave}_acao{acao_id}_select", "N/A")
                st.selectbox(f"Nova posição para ação '{current_type}'", options=list(range(1, len(listaAcoes) + 1)), index=listaAcoes.index(acao_id), key=f"{prefixoChave}_novo_pos_{acao_id}")
            if st.button("Confirmar Alterações", key=f"{prefixoChave}_confirm_reorder"):
                new_order_input = {
                    acao_id: int(st.session_state.get(f"{prefixoChave}_novo_pos_{acao_id}", listaAcoes.index(acao_id) + 1))
                    for acao_id in listaAcoes
                }
                if len(set(new_order_input.values())) != len(listaAcoes):
                    st.error("Cada ação deve ter uma posição única. Verifique as novas posições.")
                else:
                    nova_ordem = [acao for acao, pos in sorted(new_order_input.items(), key=lambda item: item[1])]
                    st.session_state[chaveListaAcoes] = nova_ordem
                    st.session_state[chaveReorder] = False
                    st.success("Ordem das ações atualizada com sucesso!")
            if st.button("Cancelar", key=f"{prefixoChave}_cancel_reorder"):
                st.session_state[chaveReorder] = False
    return listaAcoes
