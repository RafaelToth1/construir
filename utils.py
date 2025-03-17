# utils.py (versão completa com base64)
import streamlit as st
import logging
import re
import uuid

ACAO_PARAMETROS = {
    "atalho_hotkey": {
        "suffix": "_atalho",
        "formato": lambda p: f"[{p}]"
    },
    "escrever_texto": {
        "suffix": "_texto",
        "formato": lambda p: f"[{p}]"
    },
    "inserir_item_lista": {
        "suffix": "_texto",
        "formato": lambda p: f"[{p}]"
    },
    "pressionar_teclas_basicas": {
        "suffix": "_tecla",
        "formato": lambda p: f"[{p}]"
    },
    "aguardar": {
        "suffix": "_aguardar",
        "formato": lambda p: f"[{p}]"
    }
}

PREFIXO_GRUPO = lambda codigo: f"grupo{codigo}"
PREFIXO_ACOES = lambda codigo, idx: f"{PREFIXO_GRUPO(codigo)}_acoes_acao{idx}"

def obter_parametro_acao(codigoUnico, indiceAcao, tipoAcao):
    config = ACAO_PARAMETROS.get(tipoAcao)
    if not config:
        return tipoAcao
    valor = st.session_state.get(
        f"{PREFIXO_ACOES(codigoUnico, indiceAcao)}{config['suffix']}",
        ""
    )
    return f"{tipoAcao}{config['formato'](valor)}"

def processar_acoes(codigoUnico, listaAcoes, processador):
    return [
        processador(codigoUnico, indiceAcao,
                    st.session_state.get(f"{PREFIXO_ACOES(codigoUnico, indiceAcao)}_select", ""))
        for indiceAcao in listaAcoes
    ]

def processar_import_acao(codigoUnico, indice, tipoAcao, parametro):
    config = ACAO_PARAMETROS.get(tipoAcao)
    if config:
        st.session_state[
            f"{PREFIXO_ACOES(codigoUnico, indice)}{config['suffix']}"
        ] = parametro

def inicializarGrupos():
    if "ordemGrupos" not in st.session_state:
        codigoUnico = str(uuid.uuid4())
        st.session_state["ordemGrupos"] = [codigoUnico]
        logging.debug("Grupo inicial criado com codigoUnico: %s", codigoUnico)

def adicionarGrupo():
    ordemGrupos = st.session_state.get("ordemGrupos", [])
    novoCodigoUnico = str(uuid.uuid4())
    ordemGrupos.append(novoCodigoUnico)
    st.session_state["ordemGrupos"] = ordemGrupos
    logging.debug("Grupo adicionado: novoCodigoUnico=%s, ordemGrupos=%s", novoCodigoUnico, ordemGrupos)

def removerGrupo(codigoUnico):
    limparEstadoGrupo(codigoUnico)
    st.session_state["ordemGrupos"] = [g for g in st.session_state["ordemGrupos"] if g != codigoUnico]
    logging.debug("Grupo removido: codigoUnico=%s, nova ordemGrupos=%s", codigoUnico, st.session_state["ordemGrupos"])

def limparEstadoGrupo(codigoUnico):
    prefixo = f"{PREFIXO_GRUPO(codigoUnico)}_"
    for chave in list(st.session_state.keys()):
        if str(chave).startswith(prefixo) or str(chave) == f"{PREFIXO_GRUPO(codigoUnico)}_group_text":
            del st.session_state[chave]

def exportarEstado():
    relatorio = {
        "ordemGrupos": st.session_state.get("ordemGrupos", []),
        "grupos": {}
    }
    for codigoUnico in st.session_state.get("ordemGrupos", []):
        # Processa o método de busca normal
        metodo = st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_metodoBusca", "")
        if metodo == "timeout":
            timeout_val = st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_timeout_value", "2")
            metodo = f"timeout({timeout_val})"

        # Processa o método de busca para validação
        metodo_validacao = st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_metodoBuscaValidacao", "indeterminado")
        if metodo_validacao == "timeout":
            timeout_val_valid = st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_timeout_validacao", "5")
            metodo_validacao = f"timeout({timeout_val_valid})"

        dadosGrupo = {
            "metodo_busca": metodo,
            "intervalo_entre_busca": st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_intervaloBusca", ""),
            "validar_sucesso": st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_validarSucesso", "nao_validar"),
            "metodo_busca_validacao": metodo_validacao,
            "proximo_passo": st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_etapaBemSucedida", ""),
            "proximo_passo_caso_validacao_falhar": st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_etapaSemSucesso", ""),
            "imagens": st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_upload_upload_imagens", []),
            "nome_arquivo_imagem": " | ".join(
                [img['name'] for img in st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_upload_upload_imagens", [])]
            ),
            # --- CORRIGINDO A CHAVE DAS IMAGENS DE VALIDAÇÃO ---
            "imagens_validacao": st.session_state.get(f"grupo{codigoUnico}_uploadValid_upload_imagens", []),
            "nome_arquivo_imagem_validacao": " | ".join(
                [img['name'] for img in st.session_state.get(f"grupo{codigoUnico}_uploadValid_upload_imagens", [])]
            )
        }

        chaveListaAcoes = f"{PREFIXO_GRUPO(codigoUnico)}_acoes_listaAcoes"
        listaAcoes = st.session_state.get(chaveListaAcoes, [])
        dadosGrupo["procedimento_se_encontrar"] = processar_acoes(
            codigoUnico,
            listaAcoes,
            lambda codigo, idx, tipo: obter_parametro_acao(codigo, idx, tipo)
        )
        relatorio["grupos"][codigoUnico] = dadosGrupo
    return relatorio

def importarEstado(dados):
    for chave in list(st.session_state.keys()):
        if str(chave).startswith("grupo"):
            del st.session_state[chave]

    if "ordemGrupos" in dados:
        st.session_state["ordemGrupos"] = dados["ordemGrupos"]

    for codigoUnico, dadosGrupo in dados.get("grupos", {}).items():
        # Processa o método de busca normal
        mb = dadosGrupo.get("metodo_busca", "buscar_ate_encontrar")
        metodo, timeout_val = parse_timeout_field(mb, "2")
        st.session_state[f"{PREFIXO_GRUPO(codigoUnico)}_metodoBusca"] = metodo
        if metodo == "timeout":
            st.session_state[f"{PREFIXO_GRUPO(codigoUnico)}_timeout_value"] = timeout_val

        st.session_state[f"{PREFIXO_GRUPO(codigoUnico)}_intervaloBusca"] = dadosGrupo.get("intervalo_entre_busca", "1")
        st.session_state[f"{PREFIXO_GRUPO(codigoUnico)}_validarSucesso"] = dadosGrupo.get("validar_sucesso", "nao_validar")

        # Processa o método de busca para validação
        mv = dadosGrupo.get("metodo_busca_validacao", "timeout(5)")
        metodo_valid, timeout_valid_val = parse_timeout_field(mv, "5")
        st.session_state[f"{PREFIXO_GRUPO(codigoUnico)}_metodoBuscaValidacao"] = metodo_valid
        if metodo_valid == "timeout":
            st.session_state[f"{PREFIXO_GRUPO(codigoUnico)}_timeout_validacao"] = timeout_valid_val

        st.session_state[f"{PREFIXO_GRUPO(codigoUnico)}_etapaBemSucedida"] = dadosGrupo.get("proximo_passo", "")
        st.session_state[f"{PREFIXO_GRUPO(codigoUnico)}_etapaSemSucesso"] = dadosGrupo.get("proximo_passo_caso_validacao_falhar", "")

        # Processar imagens (novo formato com base64)
        chave_upload = f"{PREFIXO_GRUPO(codigoUnico)}_upload_upload_imagens"
        if "imagens" in dadosGrupo:  # Novo formato
            st.session_state[chave_upload] = dadosGrupo["imagens"]
        else:  # Compatibilidade com formato antigo
            nomes_imagens = dadosGrupo.get("nome_arquivo_imagem", "").split(" | ") if dadosGrupo.get("nome_arquivo_imagem") else []
            st.session_state[chave_upload] = [{"name": nome, "base64": ""} for nome in nomes_imagens]

        # Processar procedimentos
        procedimentos = dadosGrupo.get("procedimento_se_encontrar", [])
        chaveListaAcoes = f"{PREFIXO_GRUPO(codigoUnico)}_acoes_listaAcoes"
        st.session_state[chaveListaAcoes] = list(range(1, len(procedimentos) + 1))

        for indice, acaoCompleta in enumerate(procedimentos, start=1):
            tipoAcao, parametro = analisarAcao(acaoCompleta)
            st.session_state[f"{PREFIXO_ACOES(codigoUnico, indice)}_select"] = tipoAcao
            processar_import_acao(codigoUnico, indice, tipoAcao, parametro)

import re

def parse_timeout_field(valor, default_timeout):
    """
    Se valor for do formato timeout(4), retorna ("timeout", "4").
    Caso contrário, retorna (valor, default_timeout).
    """
    match = re.match(r'timeout\((\d+)\)', valor)
    if match:
        return "timeout", match.group(1)
    return valor, default_timeout

def analisarAcao(acaoStr):
    match = re.match(r'([^\[]+)(\[(.*)\])?', acaoStr)
    if match:
        tipo = match.group(1).strip()
        parametro = match.group(3).strip() if match.group(3) else ""
        return tipo, parametro
    return acaoStr, ""

def gerarConteudoTxt(codigoUnico):
    ordem = st.session_state.get("ordemGrupos", [])
    try:
        indiceGrupo = ordem.index(codigoUnico) + 1
    except ValueError:
        indiceGrupo = 1

    nomeEtapa = f"Etapa_{indiceGrupo}"

    # Processa imagens do upload principal
    chaveUpload = f"{PREFIXO_GRUPO(codigoUnico)}_upload_upload_imagens"
    imagensEnviadas = st.session_state.get(chaveUpload, [])
    nomeImagem = " | ".join(img['name'] for img in imagensEnviadas) if imagensEnviadas else ""

    # Processa o método de busca
    metodo = st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_metodoBusca", "")
    if metodo == "timeout":
        timeout_val = st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_timeout_value", "2")
        metodo = f"timeout({timeout_val})"

    # Processa a lista de ações
    chaveListaAcoes = f"{PREFIXO_GRUPO(codigoUnico)}_acoes_listaAcoes"
    listaAcoes = st.session_state.get(chaveListaAcoes, [])
    procedimentos = processar_acoes(
        codigoUnico,
        listaAcoes,
        lambda codigo, idx, tipo: obter_parametro_acao(codigo, idx, tipo)
    )
    procedimentosStr = " | ".join(procedimentos)

    # Processa o campo "Validar Sucesso"
    validarSucessoVal = st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_validarSucesso", "nao_validar")

    # Processa o método de busca para validação
    metodo_validacao = st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_metodoBuscaValidacao", "indeterminado")
    if metodo_validacao == "timeout":
        timeout_valid_val = st.session_state.get(f"{PREFIXO_GRUPO(codigoUnico)}_timeout_validacao", "5")
        metodo_validacao = f"timeout({timeout_valid_val})"

    # Processa as imagens de validação
    # ATENÇÃO: A chave correta é "grupo{codigoUnico}_uploadValid_upload_imagens"
    chaveUploadValid = f"grupo{codigoUnico}_uploadValid_upload_imagens"
    imagensValidacao = st.session_state.get(chaveUploadValid, [])
    imagensValidacaoNomes = " | ".join(img['name'] for img in imagensValidacao) if imagensValidacao else ""

    # Se o validar_sucesso for dos tipos que demandam imagem, inclua os nomes
    if validarSucessoVal in ["encontrar_imagem_", "nao_encontrar_imagem_"]:
        validarStr = f"{validarSucessoVal}[{imagensValidacaoNomes}]"
    else:
        validarStr = validarSucessoVal

    # Monta o conteúdo final do TXT, incluindo o campo de imagens de validação
    conteudo = [
        f"sequencia: {indiceGrupo}",
        f"nome_arquivo_imagem: {nomeImagem}",
        f"confidence: 0.8",
        f"region: none",
        f"metodo_busca: {metodo}",
        f"intervalo_entre_busca: {st.session_state.get(f'{PREFIXO_GRUPO(codigoUnico)}_intervaloBusca', '')}",
        f"procedimento_se_encontrar: {procedimentosStr}",
        f"validar_sucesso: {validarStr}",
        f"metodo_busca_validacao: {metodo_validacao}",
        f"proximo_passo: {st.session_state.get(f'{PREFIXO_GRUPO(codigoUnico)}_etapaBemSucedida', '')}",
        f"proximo_passo_caso_validacao_falhar: {st.session_state.get(f'{PREFIXO_GRUPO(codigoUnico)}_etapaSemSucesso', '')}",
        f"imagens_validacao: {imagensValidacaoNomes}"
    ]
    return "\n".join(conteudo)
