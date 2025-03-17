# --- Início de utils.py ---
import streamlit as st
import logging
import re
import uuid

ACAO_PARAMETROS = {
    "atalho_hotkey": {"suffix": "_atalho", "formato": lambda p: f"[{p}]"},
    "escrever_texto": {"suffix": "_texto", "formato": lambda p: f"[{p}]"},
    "inserir_item_lista": {"suffix": "_texto", "formato": lambda p: f"[{p}]"},
    "verificar_continuidade": {"suffix": "_texto", "formato": lambda p: f"[{p}]"},
    "pressionar_teclas_basicas": {"suffix": "_tecla", "formato": lambda p: f"[{p}]"},
    "aguardar": {"suffix": "_aguardar", "formato": lambda p: f"[{p}]"}
}

def get_group_prefix(codigo):
    return f"grupo{codigo}"

def get_group_key(codigo, key):
    return f"{get_group_prefix(codigo)}_{key}"

def get_action_key(codigo, acao_id, campo="select"):
    return f"{get_group_prefix(codigo)}_acao{acao_id}_{campo}"

PREFIXO_GRUPO = get_group_prefix
PREFIXO_ACOES = lambda codigo, acao_id: f"{PREFIXO_GRUPO(codigo)}_acao{acao_id}"

def obter_parametro_acao(codigoUnico, acao_id, tipoAcao):
    config = ACAO_PARAMETROS.get(tipoAcao)
    if not config:
        return tipoAcao
    campo = config["suffix"].lstrip("_")
    key_param = get_action_key(codigoUnico, acao_id, campo)
    valor = st.session_state.get(key_param, "")
    if tipoAcao in ["inserir_item_lista", "verificar_continuidade"] and valor == "Outro (Digite manualmente)":
        manual_key = f"{key_param}_manual"
        valor = st.session_state.get(manual_key, valor)
    return f"{tipoAcao}{config['formato'](valor)}"

def processar_acoes(codigoUnico, listaAcoes, processador):
    return [processador(codigoUnico, acao_id, st.session_state.get(get_action_key(codigoUnico, acao_id, "select"), "")) for acao_id in listaAcoes]

def processar_import_acao(codigoUnico, acao_id, tipoAcao, parametro):
    config = ACAO_PARAMETROS.get(tipoAcao)
    if config:
        st.session_state[f"{get_group_prefix(codigoUnico)}_acao{acao_id}{config['suffix']}"] = parametro

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
    st.session_state["ordemGrupos"] = [g for g in st.session_state.get("ordemGrupos", []) if g != codigoUnico]
    logging.debug("Grupo removido: codigoUnico=%s, nova ordemGrupos=%s", codigoUnico, st.session_state["ordemGrupos"])

def limparEstadoGrupo(codigoUnico):
    prefixo = f"{get_group_prefix(codigoUnico)}_"
    for chave in list(st.session_state.keys()):
        if str(chave).startswith(prefixo) or str(chave) == get_group_key(codigoUnico, "group_text"):
            del st.session_state[chave]

def exportarEstado():
    relatorio = {"ordemGrupos": st.session_state.get("ordemGrupos", []), "grupos": {}}
    for codigoUnico in relatorio["ordemGrupos"]:
        metodo = st.session_state.get(get_group_key(codigoUnico, "metodoBusca"), "")
        if metodo == "timeout":
            timeout_val = st.session_state.get(get_group_key(codigoUnico, "timeout_value"), "2")
            metodo = f"timeout({timeout_val})"
        metodo_validacao = st.session_state.get(get_group_key(codigoUnico, "metodoBuscaValidacao"), "indeterminado")
        if metodo_validacao == "timeout":
            timeout_val_valid = st.session_state.get(get_group_key(codigoUnico, "timeout_validacao"), "5")
            metodo_validacao = f"timeout({timeout_val_valid})"
        chave_upload = get_group_key(codigoUnico, "upload") + "_upload_imagens"
        chave_upload_valid = get_group_key(codigoUnico, "uploadValid") + "_upload_imagens"
        chave_lista_acoes = get_group_key(codigoUnico, "listaAcoes")
        dadosGrupo = {
            "metodo_busca": metodo,
            "intervalo_entre_busca": st.session_state.get(get_group_key(codigoUnico, "intervaloBusca"), ""),
            "validar_sucesso": st.session_state.get(get_group_key(codigoUnico, "validarSucesso"), "nao_validar"),
            "metodo_busca_validacao": metodo_validacao,
            "proximo_passo": st.session_state.get(get_group_key(codigoUnico, "etapaBemSucedida"), ""),
            "proximo_passo_caso_validacao_falhar": st.session_state.get(get_group_key(codigoUnico, "etapaSemSucesso"), ""),
            "imagens": st.session_state.get(chave_upload, []),
            "nome_arquivo_imagem": " | ".join([img['name'] for img in st.session_state.get(chave_upload, [])]),
            "imagens_validacao": st.session_state.get(chave_upload_valid, []),
            "nome_arquivo_imagem_validacao": " | ".join([img['name'] for img in st.session_state.get(chave_upload_valid, [])])
        }
        listaAcoes = st.session_state.get(chave_lista_acoes, [])
        dadosGrupo["procedimento_se_encontrar"] = processar_acoes(
            codigoUnico, listaAcoes, lambda codigo, acao_id, tipo: obter_parametro_acao(codigo, acao_id, tipo)
        )
        relatorio["grupos"][codigoUnico] = dadosGrupo
    return relatorio

def importarEstado(dados):
    for chave in [k for k in st.session_state.keys() if str(k).startswith("grupo")]:
        del st.session_state[chave]
    if "ordemGrupos" in dados:
        st.session_state["ordemGrupos"] = dados["ordemGrupos"]
    for codigoUnico, dadosGrupo in dados.get("grupos", {}).items():
        mb = dadosGrupo.get("metodo_busca", "buscar_ate_encontrar")
        metodo, timeout_val = parse_timeout_field(mb, "2")
        st.session_state[get_group_key(codigoUnico, "metodoBusca")] = metodo
        if metodo == "timeout":
            st.session_state[get_group_key(codigoUnico, "timeout_value")] = timeout_val
        st.session_state[get_group_key(codigoUnico, "intervaloBusca")] = dadosGrupo.get("intervalo_entre_busca", "1")
        st.session_state[get_group_key(codigoUnico, "validarSucesso")] = dadosGrupo.get("validar_sucesso", "nao_validar")
        mv = dadosGrupo.get("metodo_busca_validacao", "timeout(5)")
        metodo_valid, timeout_valid_val = parse_timeout_field(mv, "5")
        st.session_state[get_group_key(codigoUnico, "metodoBuscaValidacao")] = metodo_valid
        if metodo_valid == "timeout":
            st.session_state[get_group_key(codigoUnico, "timeout_validacao")] = timeout_valid_val
        st.session_state[get_group_key(codigoUnico, "etapaBemSucedida")] = dadosGrupo.get("proximo_passo", "")
        st.session_state[get_group_key(codigoUnico, "etapaSemSucesso")] = dadosGrupo.get("proximo_passo_caso_validacao_falhar", "")
        chave_upload = get_group_key(codigoUnico, "upload") + "_upload_imagens"
        if "imagens" in dadosGrupo:
            st.session_state[chave_upload] = dadosGrupo["imagens"]
        else:
            nomes_imagens = dadosGrupo.get("nome_arquivo_imagem", "").split(" | ") if dadosGrupo.get("nome_arquivo_imagem") else []
            st.session_state[chave_upload] = [{"name": nome, "base64": ""} for nome in nomes_imagens]
        procedimentos = dadosGrupo.get("procedimento_se_encontrar", [])
        chave_lista_acoes = get_group_key(codigoUnico, "listaAcoes")
        st.session_state[chave_lista_acoes] = [str(uuid.uuid4()) for _ in range(len(procedimentos))]
        for acao_id, acaoCompleta in zip(st.session_state[chave_lista_acoes], procedimentos):
            tipoAcao, parametro = analisarAcao(acaoCompleta)
            st.session_state[get_action_key(codigoUnico, acao_id, "select")] = tipoAcao
            processar_import_acao(codigoUnico, acao_id, tipoAcao, parametro)

def parse_timeout_field(valor, default_timeout):
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
    indiceGrupo = ordem.index(codigoUnico) + 1 if codigoUnico in ordem else 1
    nomeEtapa = f"Etapa_{indiceGrupo}"
    chave_upload = get_group_key(codigoUnico, "upload") + "_upload_imagens"
    imagensEnviadas = st.session_state.get(chave_upload, [])
    nomeImagem = " | ".join(img['name'] for img in imagensEnviadas) if imagensEnviadas else ""
    metodo = st.session_state.get(get_group_key(codigoUnico, "metodoBusca"), "")
    if metodo == "timeout":
        timeout_val = st.session_state.get(get_group_key(codigoUnico, "timeout_value"), "2")
        metodo = f"timeout({timeout_val})"
    chave_lista_acoes = get_group_key(codigoUnico, "listaAcoes")
    listaAcoes = st.session_state.get(chave_lista_acoes, [])
    procedimentos = processar_acoes(codigoUnico, listaAcoes, lambda codigo, acao_id, tipo: obter_parametro_acao(codigo, acao_id, tipo))
    procedimentosStr = " | ".join(procedimentos)
    validarSucessoVal = st.session_state.get(get_group_key(codigoUnico, "validarSucesso"), "nao_validar")
    metodo_validacao = st.session_state.get(get_group_key(codigoUnico, "metodoBuscaValidacao"), "indeterminado")
    if metodo_validacao == "timeout":
        timeout_valid_val = st.session_state.get(get_group_key(codigoUnico, "timeout_validacao"), "5")
        metodo_validacao = f"timeout({timeout_valid_val})"
    chave_upload_valid = get_group_key(codigoUnico, "uploadValid") + "_upload_imagens"
    imagensValidacao = st.session_state.get(chave_upload_valid, [])
    imagensValidacaoNomes = " | ".join(img['name'] for img in imagensValidacao) if imagensValidacao else ""
    validarStr = f"{validarSucessoVal}[{imagensValidacaoNomes}]" if validarSucessoVal in ["encontrar_imagem_", "nao_encontrar_imagem_"] else validarSucessoVal
    conteudo = [
        f"sequencia: {indiceGrupo}",
        f"nome_arquivo_imagem: {nomeImagem}",
        f"confidence: 0.8",
        f"region: none",
        f"metodo_busca: {metodo}",
        f"intervalo_entre_busca: {st.session_state.get(get_group_key(codigoUnico, 'intervaloBusca'), '')}",
        f"procedimento_se_encontrar: {procedimentosStr}",
        f"validar_sucesso: {validarStr}",
        f"metodo_busca_validacao: {metodo_validacao}",
        f"proximo_passo: {st.session_state.get(get_group_key(codigoUnico, 'etapaBemSucedida'), '')}",
        f"proximo_passo_caso_validacao_falhar: {st.session_state.get(get_group_key(codigoUnico, 'etapaSemSucesso'), '')}",
        f"imagens_validacao: {imagensValidacaoNomes}"
    ]
    return "\n".join(conteudo)
# --- Fim de utils.py ---
