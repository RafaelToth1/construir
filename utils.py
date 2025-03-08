# --- Início de utils.py ---
import streamlit as st
import uuid

def generate_unique_id():
    return str(uuid.uuid4())

def init_groups():
    """Inicializa a gestão dos grupos, definindo 'group_order' se não existir."""
    if "group_order" not in st.session_state:
        st.session_state["group_order"] = [0]  # inicia com o grupo 0
    # Se desejar, pode inicializar também um dicionário para dados dos grupos:
    if "groups" not in st.session_state:
        st.session_state["groups"] = {}

def add_group():
    """Adiciona um novo grupo à lista de grupos."""
    group_order = st.session_state["group_order"]
    novo_id = max(group_order) + 1 if group_order else 0
    group_order.append(novo_id)
    st.session_state["group_order"] = group_order

def remove_group(group_id):
    """Remove todas as chaves relacionadas ao grupo e atualiza a ordem dos grupos."""
    clear_group_state(group_id)
    st.session_state["group_order"] = [g for g in st.session_state["group_order"] if g != group_id]

def move_group_left(index):
    """Move o grupo da posição 'index' para a posição anterior."""
    group_order = st.session_state["group_order"]
    if index > 0:
        group_order[index-1], group_order[index] = group_order[index], group_order[index-1]
        st.session_state["group_order"] = group_order

def move_group_right(index):
    """Move o grupo da posição 'index' para a posição seguinte."""
    group_order = st.session_state["group_order"]
    if index < len(group_order) - 1:
        group_order[index], group_order[index+1] = group_order[index+1], group_order[index]
        st.session_state["group_order"] = group_order

def clear_group_state(group_id):
    """Remove todas as chaves do session_state relacionadas ao grupo."""
    for key in list(st.session_state.keys()):
        if key.startswith(f"group{group_id}_") or key == f"group{group_id}_group_text":
            del st.session_state[key]

def export_state():
    """
    Exporta o estado atual da interface, ignorando chaves que não podem ser serializadas.
    """
    report = {
        "group_order": st.session_state.get("group_order", []),
        "groups": {}
    }
    for group_id in st.session_state.get("group_order", []):
        group_data = {}
        for key, value in st.session_state.items():
            if key.startswith(f"group{group_id}_") and "file_uploader" not in key:
                if key.endswith("_add_action") or key.endswith("_remove_action"):
                    continue
                group_data[key] = value
        report["groups"][str(group_id)] = group_data
    return report

def import_state(data):
    """
    Importa o estado da interface a partir do dicionário fornecido, limpando chaves antigas e
    evitando reatribuir valores para widgets que não permitem setagem via st.session_state.
    """
    for key in list(st.session_state.keys()):
        if key.startswith("group"):
            del st.session_state[key]

    if "group_order" in data:
        st.session_state["group_order"] = data["group_order"]

    groups = data.get("groups", {})
    for group_id, group_data in groups.items():
        for key, value in group_data.items():
            if key.endswith("_add_action") or key.endswith("_remove_action"):
                continue
            st.session_state[key] = value

def generate_txt_content(group_id):
    # Nome do grupo
    group_name = st.session_state.get(f"group{group_id}_group_text", f"etapa_{group_id}")

    # Imagem (upload principal do grupo)
    uploaded_images = st.session_state.get(f"group{group_id}_upload_uploaded_images", [])
    imagem_nome = uploaded_images[0]['name'] if uploaded_images else ""

    # Ações (componente actions do grupo)
    actions_key_prefix = f"group{group_id}_actions"
    actions_list = st.session_state.get(f"{actions_key_prefix}_acoes_list", [])

    acoes = []
    for action_index in actions_list:
        acao_key = f"{actions_key_prefix}_acao{action_index}_select"
        acao_type = st.session_state.get(acao_key, "")

        # Linha principal da ação
        acoes.append(f"acao{action_index}:{acao_type}")

        # Todos os campos possíveis (mesmo vazios)
        if acao_type in ["escrever_texto", "inserir_item_lista"]:
            texto = st.session_state.get(f"{actions_key_prefix}_acao{action_index}_texto", "")
            acoes.append(f"acao{action_index}_texto:{texto}")

        elif acao_type == "atalho_hotkey":
            atalho = st.session_state.get(f"{actions_key_prefix}_acao{action_index}_atalho", "")
            acoes.append(f"acao{action_index}_atalho:{atalho}")

        elif acao_type == "pressionar_teclas_basicas":
            tecla = st.session_state.get(f"{actions_key_prefix}_acao{action_index}_tecla", "")
            acoes.append(f"acao{action_index}_tecla:{tecla}")

    # Validar (sempre incluir)
    validar = st.session_state.get(f"group{group_id}_validar", "Não")
    validar = validar.lower().replace("ã", "a")  # Converte "Não" para "nao"

    # Etapas (sempre incluir mesmo vazias)
    etapa_bem = st.session_state.get(f"group{group_id}_etapa_bem_sucedida", "")
    etapa_sem = st.session_state.get(f"group{group_id}_etapa_sem_sucesso", "")

    # Montar conteúdo do TXT
    content = [
        f"imagem:{imagem_nome}",
        "acoes:"
    ]
    content.extend(acoes)
    content.extend([
        f"validar:{validar}",
        f"etapa_bem_sucedida:{etapa_bem}",
        f"etapa_sem_sucesso:{etapa_sem}"
    ])

    return "\n".join(content)

# --- Fim de utils.py ---
