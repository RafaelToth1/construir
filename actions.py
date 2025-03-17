#actions.py
import streamlit as st
import logging
import re

CONFIG_ACOES_PADRAO = {
    "placeholder_text": "Escreva algo",
    "opcoes": [
        "", "aguardar", "avancar_item_lista", "clicar_centro", "duplo_clique_centro",
        "clicar_botao_direito", "mover_mouse_para_centro", "captura_salva_area",
        "captura_tela_completa", "atalho_hotkey", "pressionar_teclas_basicas",
        "escrever_texto", "voltar_para_etapa", "pular_para_etapa", "inserir_item_lista",
        "verificar_continuidade"
    ],
    "atalho_options": ["", "ctrl+v", "ctrl+c", "ctrl+p", "shift+left", "shift+right"],
    "teclas_basicas_options": ["", "enter", "esc", "left", "right", "win"],
}

def renderizarLinhaAcao(indiceAcao, config, prefixoChave):
    chaveSelect = f"{prefixoChave}_acao{indiceAcao}_select"
    options = config.get("opcoes", [])
    if chaveSelect not in st.session_state or st.session_state[chaveSelect] not in options:
        st.session_state[chaveSelect] = options[0]
    acao = st.selectbox(
        f"Ação {indiceAcao}",
        options,
        index=options.index(st.session_state[chaveSelect]),
        key=chaveSelect
    )
    logging.debug("Linha de ação definida: %s = %s", chaveSelect, acao)

    if acao in ["escrever_texto", "inserir_item_lista", "verificar_continuidade"]:
        chaveTexto = f"{prefixoChave}_acao{indiceAcao}_texto"
        if chaveTexto not in st.session_state:
            st.session_state[chaveTexto] = ""
        texto = st.text_input(
            "Texto",
            value=st.session_state[chaveTexto],
            placeholder=config.get("placeholder_text", "Escreva algo"),
            key=chaveTexto
        )
        logging.debug("Campo de texto para %s: %s", chaveTexto, texto)
    elif acao == "atalho_hotkey":
        chaveAtalho = f"{prefixoChave}_acao{indiceAcao}_atalho"
        if chaveAtalho not in st.session_state:
            st.session_state[chaveAtalho] = config.get("atalho_options", [])[0]
        atalho = st.selectbox(
            "Atalho",
            config.get("atalho_options", []),
            index=config.get("atalho_options", []).index(st.session_state[chaveAtalho]),
            key=chaveAtalho
        )
        logging.debug("Campo de atalho para %s: %s", chaveAtalho, atalho)
    elif acao == "pressionar_teclas_basicas":
        chaveTecla = f"{prefixoChave}_acao{indiceAcao}_tecla"
        if chaveTecla not in st.session_state:
            st.session_state[chaveTecla] = config.get("teclas_basicas_options", [])[0]
        tecla = st.selectbox(
            "Tecla",
            config.get("teclas_basicas_options", []),
            index=config.get("teclas_basicas_options", []).index(st.session_state[chaveTecla]),
            key=chaveTecla
        )
        logging.debug("Campo de tecla para %s: %s", chaveTecla, tecla)
    elif acao == "aguardar":
        chaveAguardar = f"{prefixoChave}_acao{indiceAcao}_aguardar"
        if chaveAguardar not in st.session_state:
            st.session_state[chaveAguardar] = ""
        tempo = st.text_input(
            "Tempo de espera (segundos)",
            value=st.session_state[chaveAguardar],
            placeholder="Insira um número (em segundos)",
            key=chaveAguardar
        )
        logging.debug("Campo de tempo para %s: %s", chaveAguardar, tempo)
    return acao

def removerCampoAcao(indiceAcao, prefixoChave):
    prefixo = f"{prefixoChave}_acao{indiceAcao}_"
    keysToRemove = [key for key in st.session_state if key.startswith(prefixo)]
    for key in keysToRemove:
        del st.session_state[key]
        logging.debug("Removendo chave: %s", key)

def adicionarCampoAcao(listaAcoes, indice, prefixoChave):
    novoIndiceAcao = max(listaAcoes) + 1 if listaAcoes else 1
    novaLista = listaAcoes[:indice+1] + [novoIndiceAcao] + listaAcoes[indice+1:]
    st.session_state[f"{prefixoChave}_listaAcoes"] = novaLista
    logging.debug("Adicionada nova ação: novoIndiceAcao=%s, novaLista=%s", novoIndiceAcao, novaLista)
    st.rerun()

def renderizarAreaAcoes(config=CONFIG_ACOES_PADRAO, prefixoChave=""):
    st.markdown("### Sequência de Ações")
    chaveListaAcoes = f"{prefixoChave}_listaAcoes"
    if chaveListaAcoes not in st.session_state:
        st.session_state[chaveListaAcoes] = [1]
    listaAcoes = st.session_state[chaveListaAcoes]

    for i, indiceAcao in enumerate(listaAcoes):
        cols = st.columns([4, 1, 1])
        with cols[0]:
            acao = renderizarLinhaAcao(indiceAcao, config, prefixoChave)
        with cols[1]:
            if st.button("➕", key=f"{prefixoChave}_add_{indiceAcao}"):
                adicionarCampoAcao(listaAcoes, i, prefixoChave)
        with cols[2]:
            if st.button("–", key=f"{prefixoChave}_remove_{indiceAcao}"):
                if len(listaAcoes) > 1:
                    removerCampoAcao(indiceAcao, prefixoChave)
                    novaLista = [idx for idx in listaAcoes if idx != indiceAcao]
                    st.session_state[chaveListaAcoes] = novaLista
                    logging.debug("Removida ação: indiceAcao=%s, novaLista=%s", indiceAcao, novaLista)
                    st.rerun()
                else:
                    st.warning("Pelo menos uma linha de ação é necessária.")
    return listaAcoes
