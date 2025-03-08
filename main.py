# --- Início de main.py ---
import streamlit as st
import json
from component_factory import create_component
import utils
import zipfile
from io import BytesIO

def render_group(group_id, group_index):
    st.markdown(f"#### Grupo {group_id}")
    # Nome do grupo usa índice unificado (inicia em 1)
    initial_value = f"etapa_{group_index + 1}"
    group_name = create_component("group_text", key_prefix=f"group{group_id}", initial_value=initial_value)

    create_component("upload", key_prefix=f"group{group_id}_upload")
    create_component("actions", key_prefix=f"group{group_id}_actions")

    # Botão de exclusão com confirmação
    delete_pressed = st.button("Apagar Grupo", key=f"delete_group_{group_id}")
    confirm_delete = st.checkbox("Confirmar exclusão", key=f"confirm_delete_{group_id}") if delete_pressed else False

    if confirm_delete:
        # A remoção efetiva será feita no fluxo principal (main)
        return group_name, True

    st.selectbox("Validar?", ["Não", "Sim"], key=f"group{group_id}_validar")
    st.markdown("### Upload adicional")
    create_component("upload", key_prefix=f"group{group_id}_upload_valid")
    st.selectbox("Tipo de Validação:", ["Encontrar imagem", "Não encontrar imagem"], key=f"group{group_id}_validacao_opcao")

    # Obtém nomes dos outros grupos para as etapas
    group_ids = st.session_state.get("group_order", [])
    other_names = []
    for other_id in group_ids:
        if other_id != group_id:
            nome = st.session_state.get(f"group{other_id}_group_text", f"etapa_{group_ids.index(other_id)+1}")
            other_names.append(nome)

    if other_names:
        st.selectbox("Etapa bem sucedida", options=other_names, key=f"group{group_id}_etapa_bem_sucedida")
        st.selectbox("Etapa sem sucesso", options=other_names, key=f"group{group_id}_etapa_sem_sucesso")
    else:
        st.info("Apenas um grupo disponível. Crie mais grupos para definir etapas alternativas.")

    return group_name, False

def main():
    st.set_page_config(layout="wide")
    st.title("Aplicação Dinâmica com Componentes Modulares")

    # IMPORTAÇÃO DO RELATÓRIO
    import_file = st.file_uploader("Importar Relatório", type=["json"], key="import_report")
    if import_file is not None:
        if not st.session_state.get("import_processed", False):
            try:
                data = json.load(import_file)
                utils.import_state(data)
                st.session_state["import_processed"] = True
                st.success("Relatório importado com sucesso! A aplicação será reiniciada.")
                st.rerun()
            except Exception as e:
                st.error("Erro ao importar relatório: " + str(e))
        else:
            st.info("Arquivo já importado. Para importar um novo relatório, limpe a importação abaixo.")

    # LIMPAR IMPORTAÇÃO: remove todas as chaves relacionadas à importação e grupos
    if st.button("Limpar Importação"):
        keys_to_clear = [key for key in st.session_state.keys() if key.startswith("group") or key in ["import_processed", "import_report"]]
        for key in keys_to_clear:
            del st.session_state[key]
        st.rerun()

    # Inicializa a gestão de grupos (caso ainda não exista)
    utils.init_groups()

    # EXPORTAÇÃO DO RELATÓRIO
    report = utils.export_state()
    report_json = json.dumps(report, indent=4)
    st.download_button("Exportar Relatório", data=report_json, file_name="relatorio_interface.json", mime="application/json")

    if st.button("Adicionar Grupo"):
        utils.add_group()
        st.rerun()

    group_order = st.session_state["group_order"]
    num_groups = len(group_order)
    cols = st.columns(num_groups)
    grupo_removido = False

    for i, (col, group_id) in enumerate(zip(cols, group_order)):
        with col:
            _, delete_requested = render_group(group_id, i)
            if delete_requested:
                utils.remove_group(group_id)
                grupo_removido = True

            # Botões para reordenar grupos
            col_arrow = st.columns(2)
            with col_arrow[0]:
                if i > 0 and st.button("🔙", key=f"move_left_{group_id}"):
                    utils.move_group_left(i)
                    st.rerun()
            with col_arrow[1]:
                if i < num_groups - 1 and st.button("🔜", key=f"move_right_{group_id}"):
                    utils.move_group_right(i)
                    st.rerun()

    if grupo_removido:
        st.rerun()

    # Botão para exportar TXTs
    if st.button("Exportar TXTs"):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for group_id in st.session_state.get("group_order", []):
                # Gerar conteúdo do TXT
                content = utils.generate_txt_content(group_id)
                # Obter nome do grupo para o nome do arquivo
                group_name = st.session_state.get(f"group{group_id}_group_text", f"etapa_{group_id}")
                filename = f"{group_name}.txt"
                # Adicionar ao ZIP
                zip_file.writestr(filename, content)

        # Configurar o download do ZIP
        zip_buffer.seek(0)
        st.download_button(
            label="📥 Baixar TXTs dos Grupos",
            data=zip_buffer,
            file_name="grupos.zip",
            mime="application/zip"
        )




if __name__ == "__main__":
    main()

# --- Fim de main.py ---
