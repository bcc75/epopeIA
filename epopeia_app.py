
import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from openai import OpenAI
from gtts import gTTS
import os
import tempfile
import torch
import random

st.set_page_config(
    page_title="EpopeIA",
    page_icon="https://raw.githubusercontent.com/bcc75/epopeIA/main/lcamoes2.jpeg"
)
# Adicionando CSS para definir o fundo da página como um pergaminho
st.markdown(
    f'''
    <style>
        body {{
            background-image: url("https://raw.githubusercontent.com/bcc75/epopeIA/main/fundo.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
    </style>
    ''',
    unsafe_allow_html=True
)
st.markdown("""<h1 style="font-size: 2rem; font-family: Helvetica, sans-serif; margin-bottom: 1.5rem;">
  <img src="https://raw.githubusercontent.com/bcc75/epopeIA/main/lcamoes2.jpeg" style="height: 42px; vertical-align: middle; margin-right: 12px;">
  EpopeIA — Ver com a Alma
</h1>

<div style="font-size: 1.1rem; font-family: Helvetica, sans-serif; line-height: 1.7; margin-bottom: 2rem;">
  <p>📸 <strong>Vê com os olhos</strong> — carrega uma imagem e deixa que a inteligência artificial a interprete.</p>
  <p>✍️ <strong>Ouve com a alma</strong> — a descrição torna-se um poema ao estilo de <em>Camões</em>.</p>
  <p>📜 <strong>Poesia assistiva</strong> — uma ponte entre a visão e a palavra, entre o passado e o futuro.</p>
  <p>⛵ <strong>EpopeIA</strong> navega entre pixels e versos, com a alma lusitana sempre ao leme.</p>
</div>""", unsafe_allow_html=True)

def carregar_base(tom):
    if tom == "⚔️ Épico":
        caminho = "camoes_epico.txt"
    else:
        caminho = "camoes_lirico.txt"
    with open(caminho, "r", encoding="utf-8") as f:
        versos = f.read().strip().split("\n\n")
    return random.sample(versos, min(3, len(versos)))

openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key) if openai_key else None

def traduzir_descricao(desc):
    if not desc:
        return ""
    palavras_ingles = ["sun", "sea", "photo", "image", "man", "woman", "sky", "tree", "people", "walking", "road"]
    if any(p in desc.lower() for p in palavras_ingles):
        traducao = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Traduz para português de Portugal, de forma natural e literária."},
                {"role": "user", "content": desc}
            ],
            temperature=0.3
        )
        return traducao.choices[0].message.content.strip()
    return desc

def gerar_audio_gtts(texto):
    tts = gTTS(texto, lang="pt", tld="pt")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
        tts.save(out.name)
        return out.name

@st.cache_resource(show_spinner=False)
def load_blip():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to("cuda" if torch.cuda.is_available() else "cpu")
    return processor, model

processor, model = load_blip()

def gerar_descricao(imagem):
    inputs = processor(imagem, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

uploaded_file = st.file_uploader("📷 Carrega uma imagem (JPG/PNG, até 200MB)", type=["jpg", "jpeg", "png"])
st.caption("🛈 No iOS, o áudio pode requerer clique manual. A câmara nem sempre é ativada por segurança do browser.")

tom = st.radio("🎭 Escolhe o tom do poema:", ["⚔️ Épico", "🌹 Romântico"])

if uploaded_file and client:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem carregada", use_container_width=True)

    with st.spinner("🧠 A interpretar a imagem..."):
        descricao_ingles = gerar_descricao(image)
        descricao = traduzir_descricao(descricao_ingles)
        st.success(f"Descrição: *{descricao}*")

    excertos = carregar_base(tom)
    exemplos = "\n\n".join(excertos)

    prompt = f"""
Tu és Luís de Camões. A tua missão é transformar uma descrição visual num poema com tom {tom.replace("⚔️", "").replace("🌹", "").strip().lower()}, escrito em português do século XVI.

Inspira-te nestes exemplos reais do teu estilo:

{exemplos}

Agora, escreve um poema com um verso por linha, e com quebras de linha entre estrofes. Usa linguagem clássica, rica, com ritmo, e vocabulário do século XVI.

Descrição:
{descricao}

Poema:
"""

    with st.spinner("✍️ A gerar poema camoniano..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Escreve como Luís de Camões. Usa vocabulário do século XVI, metáforas clássicas, ritmo lírico português. Adapta o tom consoante o pedido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        poema = response.choices[0].message.content.strip()
        st.markdown(f"📝 **Poema ({tom}):**")
        st.text(poema)

        with st.spinner("🎧 A gerar voz..."):
            audio_path = gerar_audio_gtts(poema)
            st.audio(audio_path, format="audio/mp3")
            with open(audio_path, "rb") as f:
                st.download_button("⬇️ Descarregar áudio", f, file_name="camoes_poema.mp3")


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


if uploaded_file and 'poema' in locals():
    imagem_final = gerar_imagem_com_poema(uploaded_file.name, poema)
    txt_final = gerar_txt_poema(poema)

    st.download_button("📝 Descarregar poema em texto", open(txt_final, "rb"), file_name="poema.txt", mime="text/plain")
