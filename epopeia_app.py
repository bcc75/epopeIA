
import streamlit as st
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.title("🌊 EpopeIA — Ver com a Alma")

# Função para gerar imagem com poema sobreposto
def gerar_imagem_com_poema(imagem_path, poema_texto):
    imagem_original = Image.open(imagem_path)
    largura, altura = imagem_original.size

    fundo = Image.new("RGB", (largura, altura + 200), (245, 222, 179))  # Fundo bege
    fundo.paste(imagem_original, (0, 0))

    draw = ImageDraw.Draw(fundo)
    font_titulo = ImageFont.load_default()
    font_poema = ImageFont.load_default()

    draw.text((50, altura + 20), "Poema Inspirado", fill=(139, 69, 19), font=font_titulo)

    linhas = textwrap.wrap(poema_texto, width=50)
    y_text = altura + 70
    for linha in linhas:
        draw.text((50, y_text), linha, fill=(80, 40, 20), font=font_poema)
        y_text += 40

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

    st.image(imagem_path, caption="Imagem carregada", use_column_width=True)

    # Exemplo de poema
    poema_texto = """Ó mar bravio, de espuma coroado,
    Guia naus e sonhos pelo destino traçado.
    O vento canta, no peito esperança,
    Ecoando glórias de heroica lembrança."""

    # Gerar imagem e ficheiro TXT
    imagem_final = gerar_imagem_com_poema(imagem_path, poema_texto)
    txt_final = gerar_txt_poema(poema_texto)

    # Botões de download
    st.download_button("📸 Descarregar imagem com poema", open(imagem_final, "rb"), file_name="poema_imagem.png", mime="image/png")
    st.download_button("📝 Descarregar poema em texto", open(txt_final, "rb"), file_name="poema.txt", mime="text/plain")
