# main.py

import streamlit as st
import json
import zipfile
from io import BytesIO
from component_factory import criarComponente
import utils
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def processar_upload(arquivos, func_importar, chave_flag, mensagem_sucesso, tipo_relatorio, multiple=False):
    if arquivos is not None:
        if not st.session_state.get(chave_flag, False):
            try:
                if multiple:
                    for arquivo in arquivos:
                        if tipo_relatorio == "json":
                            dados = json.load(arquivo)
                            func_importar(dados)
                else:
                    if tipo_relatorio == "json":
                        dados = json.load(arquivos)
                        func_importar(dados)
                st.session_state[chave_flag] = True
                st.success(mensagem_sucesso)
                st.rerun()
            except Exception as erro:
                st.error(f"Erro ao importar relatório: {erro}")
        else:
            st.info("Arquivo já importado. Para importar um novo relatório, limpe a importação abaixo.")

def renderizarUpload(codigoUnico):
    criarComponente("upload", prefixoChave=f"grupo{codigoUnico}_upload")

def renderizarConfiguracoesBusca(codigoUnico):
    st.markdown("### Configurações de Busca")
    metodo_busca = st.selectbox(
        "Método de busca",
        ["timeout", "buscar_ate_encontrar", "tempo_indeterminado"],
        index=1,
        key=f"grupo{codigoUnico}_metodoBusca"
    )

    # Exibe a caixa de texto para informar o tempo apenas se "timeout" for selecionado
    if metodo_busca == "timeout":
        st.text_input(
            "Número de segundos para timeout",
            value="2",
            key=f"grupo{codigoUnico}_timeout_value",
            placeholder="Digite o número de segundos"
        )

    st.text_input(
        "Intervalo entre buscas",
        value="1",
        key=f"grupo{codigoUnico}_intervaloBusca",
        placeholder="Digite um número de 1 a 10"
    )


def renderizarAcoes(codigoUnico):
    criarComponente("actions", prefixoChave=f"grupo{codigoUnico}_acoes")

def renderizarValidacao(codigoUnico):
    st.markdown("### Seção de validação (após executar as ações dessa etapa)")
    st.selectbox(
        "Validar sucesso",
        ["nao_validar", "encontrar_imagem_", "nao_encontrar_imagem_"],
        key=f"grupo{codigoUnico}_validarSucesso"
    )
    criarComponente("upload", prefixoChave=f"grupo{codigoUnico}_uploadValid")

    # Atualize aqui o selectbox para exibir "timeout" sem os parênteses
    metodo_validacao = st.selectbox(
        "Método de busca validação",
        ["timeout", "indeterminado"],
        key=f"grupo{codigoUnico}_metodoBuscaValidacao"
    )

    # Se o método escolhido for "timeout", exibe a caixa para definir os segundos
    if metodo_validacao == "timeout":
        st.text_input(
            "Número de segundos para timeout (validação)",
            value="5",
            key=f"grupo{codigoUnico}_timeout_validacao",
            placeholder="Digite o número de segundos"
        )

    ordemGrupos = st.session_state.get("ordemGrupos", [])
    outrasEtapas = []
    for outroCodigo in ordemGrupos:
        if outroCodigo != codigoUnico:
            indiceOutro = ordemGrupos.index(outroCodigo) + 1
            outrasEtapas.append(f"Etapa_{indiceOutro}")
    if outrasEtapas:
        st.selectbox("Etapa bem sucedida", options=outrasEtapas, key=f"grupo{codigoUnico}_etapaBemSucedida")
        st.selectbox("Etapa sem sucesso", options=outrasEtapas, key=f"grupo{codigoUnico}_etapaSemSucesso")
    else:
        st.info("Apenas uma etapa disponível. Crie mais etapas para definir próximos passos.")

def renderizarControlesGrupo(codigoUnico):
    remover = False
    if st.button("Apagar Etapa", key=f"delete_grupo_{codigoUnico}"):
        st.session_state[f"show_confirm_{codigoUnico}"] = True
    if st.session_state.get(f"show_confirm_{codigoUnico}", False):
        confirmarExclusao = st.checkbox("Confirmar exclusão", key=f"confirm_delete_{codigoUnico}")
        if confirmarExclusao:
            remover = True
    return remover

def renderizarEtapa(codigoUnico, indiceGrupo):
    st.markdown(f"#### Etapa_{indiceGrupo + 1}")
    renderizarUpload(codigoUnico)
    renderizarConfiguracoesBusca(codigoUnico)
    renderizarAcoes(codigoUnico)
    renderizarValidacao(codigoUnico)
    return renderizarControlesGrupo(codigoUnico)


def principal():
    st.set_page_config(layout="wide")
    st.title("Aplicação Dinâmica com Componentes Modulares")

    # Upload dos relatórios (JSON)
    arquivoImportacao = st.file_uploader("Importar Relatório", type=["json"], key="import_report")
    processar_upload(
        arquivoImportacao,
        utils.importarEstado,
        "import_processed",
        "Relatório importado com sucesso! A aplicação será reiniciada.",
        "json"
    )

    if st.button("Limpar Importação"):
        chavesLimpar = [
            chave for chave in st.session_state.keys()
            if str(chave).startswith("grupo") or chave in [
                "import_processed", "import_report"
            ]
        ]
        for chave in chavesLimpar:
            del st.session_state[chave]
        st.rerun()

    # Inicializa os grupos se necessário
    utils.inicializarGrupos()
    ordemGrupos = st.session_state["ordemGrupos"]
    numEtapas = len(ordemGrupos)
    colunas = st.columns(numEtapas)
    removerAlguma = False

    # Renderiza cada grupo sem os botões de setas de movimentação
    for i, (col, codigoUnico) in enumerate(zip(colunas, ordemGrupos)):
        with col:
            if renderizarEtapa(codigoUnico, i):
                utils.removerGrupo(codigoUnico)
                removerAlguma = True

    if removerAlguma:
        st.rerun()

    # Botões de adicionar e exportar etapas
    colAdicionar, colExportarRelatorio, colExportarTxts = st.columns(3)
    with colAdicionar:
        if st.button("Adicionar Etapa"):
            utils.adicionarGrupo()
            st.rerun()
    with colExportarRelatorio:
        relatorio = utils.exportarEstado()
        relatorioJson = json.dumps(relatorio, indent=4)
        st.download_button(
            "Exportar Relatório",
            data=relatorioJson,
            file_name="relatorio_interface.json",
            mime="application/json"
        )
    with colExportarTxts:
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
            st.download_button(
                label="📥 Baixar TXTs das Etapas",
                data=bufferZip,
                file_name="etapas.zip",
                mime="application/zip"
            )

    # NOVA INTERFACE DE REORDENAÇÃO DE GRUPOS
    st.markdown("### Reordenação de Grupos")
    if st.button("Reordenar Grupos"):
        st.session_state["mostrar_reordenacao"] = True

    if st.session_state.get("mostrar_reordenacao", False):
        ordem_atual = st.session_state.get("ordemGrupos", [])
        st.write("Ordem atual dos grupos:", ordem_atual)
        new_order_input = {}
        for codigo in ordem_atual:
            new_pos = st.selectbox(
                f"Nova posição para o grupo {codigo}",
                options=list(range(1, len(ordem_atual) + 1)),
                index=ordem_atual.index(codigo),
                key=f"novo_pos_{codigo}"
            )
            new_order_input[codigo] = new_pos
        if st.button("Confirmar Alterações"):
            if len(set(new_order_input.values())) != len(ordem_atual):
                st.error("Cada grupo deve ter uma posição única. Verifique as novas posições.")
            else:
                nova_ordem = [codigo for codigo, pos in sorted(new_order_input.items(), key=lambda item: item[1])]
                st.session_state["ordemGrupos"] = nova_ordem
                st.success("Ordem atualizada com sucesso!")
                st.session_state["mostrar_reordenacao"] = False
                st.rerun()

if __name__ == "__main__":
    principal()
