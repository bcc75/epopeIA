
import streamlit as st
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.set_page_config(
    page_title="EpopeIA",
    page_icon="https://raw.githubusercontent.com/bcc75/epopeIA/main/lcamoes2.jpeg"
)

# Função para redimensionar a imagem apenas para o poema (thumbnail)
def redimensionar_imagem(imagem_path):
    imagem = Image.open(imagem_path)
    imagem.thumbnail((300, 300))  # Redimensionar para 300x300
    novo_caminho = "imagem_thumbnail.png"
    imagem.save(novo_caminho)
    return novo_caminho

# Função para gerar imagem com poema sobreposto
def gerar_imagem_com_poema(imagem_path, poema_texto):
    imagem_thumbnail = redimensionar_imagem(imagem_path)  # Criar versão reduzida para o poema
    imagem_original = Image.open(imagem_thumbnail)
    largura, altura = imagem_original.size

    fundo = Image.new("RGB", (largura, altura + 200), (245, 222, 179))  # Fundo bege
    fundo.paste(imagem_original, (50, 30))  # Posicionar imagem

    draw = ImageDraw.Draw(fundo)
    font_titulo = ImageFont.load_default()
    font_poema = ImageFont.load_default()

    draw.text((50, altura + 40), "Poema Inspirado", fill=(139, 69, 19), font=font_titulo)

    linhas = textwrap.wrap(poema_texto, width=40)
    y_text = altura + 80
    for linha in linhas:
        draw.text((50, y_text), linha, fill=(80, 40, 20), font=font_poema)
        y_text += 30

    caminho_saida = "poema_imagem.png"
    fundo.save(caminho_saida)
    return caminho_saida

# Função para gerar ficheiro TXT com o poema
def gerar_txt_poema(poema_texto):
    caminho_txt = "poema.txt"
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write("EpopeIA — Ver com a Alma\n")
        f.write("=" * 30 + "\n\n")
        f.write(poema_texto + "\n")
    return caminho_txt

# Interface para carregar imagem
uploaded_file = st.file_uploader("📷 Carrega uma imagem", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Salvar a imagem carregada temporariamente antes do processamento
    imagem_path = "imagem_carregada.png"
    with open(imagem_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(imagem_path, caption="Imagem carregada", use_container_width=True)

    # Simulação de um poema gerado
    poema = """Ó mar bravio, de espuma coroado,
    Guia naus e sonhos pelo destino traçado.
    O vento canta, no peito esperança,
    Ecoando glórias de heroica lembrança.""" 

    # Gerar imagem e ficheiro TXT
    imagem_final = gerar_imagem_com_poema(imagem_path, poema)
    txt_final = gerar_txt_poema(poema)

    # Botões de download
    st.download_button("📸 Descarregar imagem com poema", open(imagem_final, "rb"), file_name="poema_imagem.png", mime="image/png")
    st.download_button("📝 Descarregar poema em texto", open(txt_final, "rb"), file_name="poema.txt", mime="text/plain")
