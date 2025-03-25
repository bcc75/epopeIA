
import streamlit as st
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.title("🌊 EpopeIA — Ver com a Alma")

# Função para redimensionar a imagem antes de gerar o poema
def redimensionar_imagem(imagem_path):
    imagem = Image.open(imagem_path)
    imagem.thumbnail((300, 300))  # Redimensionar para 300x300
    novo_caminho = "imagem_redimensionada.png"
    imagem.save(novo_caminho)
    return novo_caminho

# Função para gerar imagem com poema sobreposto
def gerar_imagem_com_poema(imagem_path, poema_texto):
    imagem_original = Image.open(imagem_path)
    largura, altura = imagem_original.size

    fundo = Image.new("RGB", (largura, altura + 200), (245, 222, 179))  # Fundo bege
    fundo.paste(imagem_original, (50, 30))  # Posicionar imagem com margem

    draw = ImageDraw.Draw(fundo)
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
        font_titulo = ImageFont.truetype(font_path, 30)
        font_poema = ImageFont.truetype(font_path, 24)
    except:
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

# Função para gerar ficheiro TXT
def gerar_txt_poema(poema_texto):
    caminho_txt = "poema.txt"
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write("EpopeIA — Ver com a Alma\n")
        f.write("=" * 30 + "\n\n")
        f.write(poema_texto + "\n")
    return caminho_txt

# Interface para carregar imagem
imagem_upload = st.file_uploader("📷 Carrega uma imagem", type=["png", "jpg", "jpeg"])

if imagem_upload:
    imagem_path = "imagem_carregada.png"
    with open(imagem_path, "wb") as f:
        f.write(imagem_upload.getbuffer())

    # Redimensionar imagem para não ocupar todo o ficheiro final
    imagem_path_redimensionada = redimensionar_imagem(imagem_path)

    st.image(imagem_path_redimensionada, caption="Imagem carregada", use_container_width=True)

    # Exemplo de poema
    poema_texto = """Ó mar bravio, de espuma coroado,
    Guia naus e sonhos pelo destino traçado.
    O vento canta, no peito esperança,
    Ecoando glórias de heroica lembrança.""" 

    # Gerar imagem e ficheiro TXT
    imagem_final = gerar_imagem_com_poema(imagem_path_redimensionada, poema_texto)
    txt_final = gerar_txt_poema(poema_texto)

    # Botões de download
    st.download_button("📸 Descarregar imagem com poema", open(imagem_final, "rb"), file_name="poema_imagem.png", mime="image/png")
    st.download_button("📝 Descarregar poema em texto", open(txt_final, "rb"), file_name="poema.txt", mime="text/plain")


# Função para redimensionar a imagem apenas para o poema (thumbnail)
def redimensionar_imagem(imagem_path):
    imagem = Image.open(imagem_path)
    imagem.thumbnail((300, 300))  # Redimensionar para 300x300
    novo_caminho = "imagem_thumbnail.png"
    imagem.save(novo_caminho)
    return novo_caminho

# Função para gerar imagem com poema sobreposto
def gerar_imagem_com_poema(imagem_path, poema_texto):
    imagem_path = redimensionar_imagem(imagem_path)  # Redimensionar apenas para o poema
    imagem_original = Image.open(imagem_path)
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


if uploaded_file:
    imagem_final = gerar_imagem_com_poema(uploaded_file.name, poema)
    txt_final = gerar_txt_poema(poema)

    st.download_button("📸 Descarregar imagem com poema", open(imagem_final, "rb"), file_name="poema_imagem.png", mime="image/png")
    st.download_button("📝 Descarregar poema em texto", open(txt_final, "rb"), file_name="poema.txt", mime="text/plain")
