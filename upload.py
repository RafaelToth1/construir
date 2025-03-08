# --- Início de upload.py ---
import streamlit as st
from PIL import Image
import base64
from io import BytesIO

DEFAULT_UPLOAD_CONFIG = {
    "label": "Carregar imagens",
    "tipos": ["png", "jpg", "jpeg"],
    "multiple": True,
    "width": 100,
    "max_size": 2 * 1024 * 1024  # 2 MB
}

def convert_image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def render_upload_area(config: dict = DEFAULT_UPLOAD_CONFIG, key_prefix: str = ""):
    label = config.get("label", "Carregar imagens")
    file_types = config.get("tipos", ["png", "jpg", "jpeg"])
    multiple = config.get("multiple", True)
    width = config.get("width", 100)
    max_size = config.get("max_size", 2 * 1024 * 1024)

    arquivos = st.file_uploader(label, type=file_types, accept_multiple_files=multiple, key=f"{key_prefix}_file_uploader")
    state_key = f"{key_prefix}_uploaded_images"
    if state_key not in st.session_state:
        st.session_state[state_key] = []

    if arquivos:
        for arquivo in arquivos:
            if arquivo.size > max_size:
                st.error(f"O arquivo {arquivo.name} excede o tamanho máximo permitido (2 MB).")
                continue
            exists = any(img.get("name") == arquivo.name for img in st.session_state[state_key])
            if not exists:
                try:
                    image = Image.open(arquivo)
                    img_base64 = convert_image_to_base64(image)
                    st.session_state[state_key].append({
                        "name": arquivo.name,
                        "base64": img_base64
                    })
                except Exception as e:
                    st.error(f"Erro ao carregar {arquivo.name}: {e}")

    uploaded_images = st.session_state.get(state_key, [])
    if uploaded_images:
        st.markdown("### Imagens")
        for img in uploaded_images:
            img_bytes = base64.b64decode(img["base64"])
            st.image(img_bytes, caption=img["name"], width=width)

    return arquivos


# --- Fim de upload.py ---
