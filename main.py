#main.py
import streamlit as st
import json
import zipfile
from io import BytesIO
from component_factory import criarComponente
import utils
import logging
import pandas as pd
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def processar_upload(arquivos, func_importar, chave_flag, mensagem_sucesso, tipo_relatorio, multiple=False):
    if arquivos:
        if not st.session_state.get(chave_flag, False):
            try:
                arquivos_list = arquivos if multiple else [arquivos]
                for arquivo in arquivos_list:
                    if tipo_relatorio == "json":
                        dados = json.load(arquivo)
                        func_importar(dados)
                st.session_state[chave_flag] = True
                st.success(mensagem_sucesso)
                st.rerun()
            except Exception as erro:
                st.error(f"Erro ao importar relatório: {erro}")
        else:
            st.info("Arquivo já importado. Para importar um novo relatório, limpe a importação abaixo.")

def renderizarUpload(codigoUnico):
    criarComponente("upload", prefixoChave=utils.get_group_key(codigoUnico, "upload"))

def _render_input(key, label, value, placeholder, disabled=False):
    st.text_input(label, value=value, key=key, placeholder=placeholder, disabled=disabled)

def renderizarConfiguracoesBusca(codigoUnico):
    st.markdown("### Configurações de Busca")
    cols = st.columns(3)
    metodo_busca = cols[0].selectbox("Método de busca", ["timeout", "buscar_ate_encontrar", "tempo_indeterminado"], index=1, key=utils.get_group_key(codigoUnico, "metodoBusca"))
    configs = [
        {'key_suffix': "timeout_value", 'label': "Número de segundos para timeout", 'disabled': metodo_busca != "timeout", 'default': "2", 'placeholder': "Digite o número de segundos"},
        {'key_suffix': "intervaloBusca", 'label': "Intervalo entre buscas", 'disabled': False, 'default': "1", 'placeholder': "Digite um número de 1 a 10"}
    ]
    for col, config in zip(cols[1:], configs):
        with col:
            _render_input(utils.get_group_key(codigoUnico, config['key_suffix']), config['label'], config['default'], config['placeholder'], disabled=config['disabled'])

def renderizarAcoes(codigoUnico):
    criarComponente("actions", prefixoChave=utils.get_group_prefix(codigoUnico))

def renderizarValidacao(codigoUnico):
    st.markdown("### Seção de validação (após executar as ações dessa etapa)")
    st.selectbox("Validar sucesso", ["nao_validar", "encontrar_imagem_", "nao_encontrar_imagem_"], key=utils.get_group_key(codigoUnico, "validarSucesso"))
    criarComponente("upload", prefixoChave=utils.get_group_key(codigoUnico, "uploadValid"))
    metodo_validacao = st.selectbox("Método de busca validação", ["timeout", "indeterminado"], key=utils.get_group_key(codigoUnico, "metodoBuscaValidacao"))
    if metodo_validacao == "timeout":
        st.text_input("Número de segundos para timeout (validação)", value="5", key=utils.get_group_key(codigoUnico, "timeout_validacao"), placeholder="Digite o número de segundos")
    ordemGrupos = st.session_state.get("ordemGrupos", [])
    outrasEtapas = [f"Etapa_{ordemGrupos.index(outroCodigo) + 1}" for outroCodigo in ordemGrupos if outroCodigo != codigoUnico]
    if outrasEtapas:
        st.selectbox("Etapa bem sucedida", options=outrasEtapas, key=utils.get_group_key(codigoUnico, "etapaBemSucedida"))
        st.selectbox("Etapa sem sucesso", options=outrasEtapas, key=utils.get_group_key(codigoUnico, "etapaSemSucesso"))
    else:
        st.info("Apenas uma etapa disponível. Crie mais etapas para definir próximos passos.")

def renderizarEtapa(codigoUnico, indiceGrupo):
    remover = False
    header_cols = st.columns([8, 2])
    with header_cols[0]:
        st.markdown(f"#### Etapa_{indiceGrupo + 1}")
    with header_cols[1]:
        if st.button("Apagar Etapa", key=f"delete_grupo_{codigoUnico}"):
            st.session_state[f"show_confirm_{codigoUnico}"] = True
        if st.session_state.get(f"show_confirm_{codigoUnico}", False):
            confirmarExclusao = st.checkbox("Confirmar exclusão", key=f"confirm_delete_{codigoUnico}")
            if confirmarExclusao:
                remover = True
    renderizarUpload(codigoUnico)
    renderizarConfiguracoesBusca(codigoUnico)
    renderizarAcoes(codigoUnico)
    renderizarValidacao(codigoUnico)
    return remover

def render_sidebar_file_viewer():
    with st.sidebar:
        st.header("Visualizador de Cabeçalhos")
        uploaded_file = st.file_uploader("Escolha um arquivo XLSX ou CSV", type=["xlsx", "csv"], key="file_viewer_upload")
        if uploaded_file is not None:
            file_name = os.path.splitext(uploaded_file.name)[0]
            try:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.sidebar.subheader("Formato solicitado:")
                formatos = [f"{file_name}, {col}" for col in df.columns]
                st.session_state["formatos_solicitados"] = formatos
                for formato in formatos:
                    st.sidebar.text(formato)
            except Exception as e:
                st.sidebar.error(f"Erro ao processar o arquivo: {e}")

def reordenar_grupos():
    ordem_atual = st.session_state.get("ordemGrupos", [])
    st.markdown("### Reordenação de Grupos")
    st.write("Ordem atual dos grupos:", ordem_atual)
    new_order_input = {}
    for codigo in ordem_atual:
        new_order_input[codigo] = st.selectbox(f"Nova posição para o grupo {codigo}", options=list(range(1, len(ordem_atual) + 1)), index=ordem_atual.index(codigo), key=f"novo_pos_{codigo}")
    if st.button("Confirmar Alterações"):
        if len(set(new_order_input.values())) != len(ordem_atual):
            st.error("Cada grupo deve ter uma posição única. Verifique as novas posições.")
        else:
            nova_ordem = [codigo for codigo, pos in sorted(new_order_input.items(), key=lambda item: item[1])]
            st.session_state["ordemGrupos"] = nova_ordem
            st.success("Ordem atualizada com sucesso!")
            st.session_state["mostrar_reordenacao"] = False

def principal():
    st.title("Aplicação Dinâmica com Componentes Modulares")
    with st.sidebar:
        st.header("Controles Gerais")
        arquivoImportacao = st.file_uploader("Importar Relatório", type=["json"], key="import_report")
        processar_upload(arquivoImportacao, utils.importarEstado, "import_processed", "Relatório importado com sucesso! A aplicação será reiniciada.", "json")
        if st.button("Limpar Importação"):
            chavesLimpar = [chave for chave in st.session_state.keys() if str(chave).startswith("grupo") or chave in ["import_processed", "import_report"]]
            for chave in chavesLimpar:
                del st.session_state[chave]
            st.rerun()
        if st.button("Reordenar Grupos"):
            st.session_state["mostrar_reordenacao"] = True
        relatorio = utils.exportarEstado()
        relatorioJson = json.dumps(relatorio, indent=4)
        st.download_button("Exportar Relatório", data=relatorioJson, file_name="relatorio_interface.json", mime="application/json")
        if st.button("Exportar TXTs"):
            bufferZip = BytesIO()
            with zipfile.ZipFile(bufferZip, 'w', zipfile.ZIP_DEFLATED) as arquivoZip:
                for codigoUnico in st.session_state.get("ordemGrupos", []):
                    conteudo = utils.gerarConteudoTxt(codigoUnico)
                    indiceGrupo = st.session_state["ordemGrupos"].index(codigoUnico) + 1
                    nomeEtapa = f"Etapa_{indiceGrupo}"
                    nomeArquivo = f"{nomeEtapa}.txt"
                    arquivoZip.writestr(nomeArquivo, conteudo)
            bufferZip.seek(0)
            st.download_button(label="Baixar TXTs das Etapas", data=bufferZip, file_name="etapas.zip", mime="application/zip")
        if st.button("Adicionar Etapa"):
            utils.adicionarGrupo()
        if st.session_state.get("mostrar_reordenacao", False):
            reordenar_grupos()
    render_sidebar_file_viewer()
    utils.inicializarGrupos()
    ordemGrupos = st.session_state["ordemGrupos"]
    abas = st.tabs([f"Etapa {i+1}" for i in range(len(ordemGrupos))])
    removerAlguma = False
    for i, (aba, codigoUnico) in enumerate(zip(abas, ordemGrupos)):
        with aba:
            if renderizarEtapa(codigoUnico, i):
                utils.removerGrupo(codigoUnico)
                removerAlguma = True
    if removerAlguma:
        st.rerun()

if __name__ == "__main__":
    principal()
