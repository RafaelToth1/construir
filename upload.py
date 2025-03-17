# upload.py
import streamlit as st
from PIL import Image
import base64
from io import BytesIO

CONFIG_UPLOAD_PADRAO = {
    "label": "Carregar imagens",
    "tipos": ["png", "jpg", "jpeg"],
    "multiple": True,
    "width": 100,
    "max_size": 2 * 1024 * 1024  # 2 MB
}

def converterImagemParaBase64(imagem: Image.Image) -> str:
    buffer = BytesIO()
    imagem.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def processarUpload(config: dict, prefixoChave: str):
    rotulo = config.get("label", "Carregar imagens")
    tiposArquivos = config.get("tipos", ["png", "jpg", "jpeg"])
    permitirMultiplos = config.get("multiple", True)
    tamanhoMaximo = config.get("max_size", 2 * 1024 * 1024)
    arquivos = st.file_uploader(rotulo, type=tiposArquivos, accept_multiple_files=permitirMultiplos, key=f"{prefixoChave}_fileUploader")
    chaveEstado = f"{prefixoChave}_upload_imagens"
    if chaveEstado not in st.session_state:
        st.session_state[chaveEstado] = []
    if arquivos:
        for arquivo in arquivos:
            if arquivo.size > tamanhoMaximo:
                st.error(f"O arquivo {arquivo.name} excede o tamanho máximo permitido (2 MB).")
                continue
            jaExiste = any(img.get("name") == arquivo.name for img in st.session_state[chaveEstado])
            if not jaExiste:
                try:
                    imagem = Image.open(arquivo)
                    imgBase64 = converterImagemParaBase64(imagem)
                    st.session_state[chaveEstado].append({
                        "name": arquivo.name,
                        "base64": imgBase64
                    })
                except Exception as erro:
                    st.error(f"Erro ao carregar {arquivo.name}: {erro}")
    return arquivos

def renderizarImagens(prefixoChave: str, largura: int):
    chaveEstado = f"{prefixoChave}_upload_imagens"
    imagensEnviadas = st.session_state.get(chaveEstado, [])
    if imagensEnviadas:
        st.markdown("### Imagens")
        for img in imagensEnviadas:
            imgBytes = base64.b64decode(img["base64"])
            st.image(imgBytes, caption=img["name"], width=largura)

def renderizarAreaUpload(config: dict = CONFIG_UPLOAD_PADRAO, prefixoChave: str = ""):
    processarUpload(config, prefixoChave)
    renderizarImagens(prefixoChave, config.get("width", 100))
