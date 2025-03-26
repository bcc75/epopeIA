
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from transformers import BlipProcessor, BlipForConditionalGeneration
from openai import OpenAI
from gtts import gTTS
import os
import tempfile
import torch
import random
from datetime import datetime

st.set_page_config(
    page_title="EpopeIA",
    page_icon="https://raw.githubusercontent.com/bcc75/epopeIA/main/lcamoes2.jpeg"
)

# Adicionar CSS para definir o fundo da página como um pergaminho
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

def gerar_titulo_poema(descricao):
    prompt_titulo = f"Cria um título épico e poético, ao estilo de Camões, para um poema baseado nesta descrição: {descricao}"
    resposta_titulo = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Gera um título curto, épico e poético."},
                  {"role": "user", "content": prompt_titulo}],
        temperature=0.7,
        max_tokens=20
    )
    return resposta_titulo.choices[0].message.content.strip()

uploaded_file = st.file_uploader("📷 Carrega uma imagem (JPG/PNG, até 200MB)", type=["jpg", "jpeg", "png"])
st.caption("🛈 No iOS, o áudio pode requerer clique manual. A câmara nem sempre é ativada por segurança do browser.")

tom = st.radio("🎭 Escolhe o tom do poema:", ["⚔️ Épico", "🌹 Romântico"])

if uploaded_file and client:
    imagem_path = "imagem_carregada.png"
    with open(imagem_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    image = Image.open(imagem_path).convert("RGB")
    st.image(image, caption="Imagem carregada", use_container_width=True)

    with st.spinner("🧠 A interpretar a imagem..."):
        descricao_ingles = gerar_descricao(image)
        descricao = traduzir_descricao(descricao_ingles)
        st.success(f"Descrição: *{descricao}*")

    titulo_poema = gerar_titulo_poema(descricao)

    excertos = carregar_base(tom)
    exemplos = "\n\n".join(excertos)

    prompt = f"""Tu és Luís de Camões. A tua missão é transformar uma descrição visual num poema com tom {tom.replace("⚔️", "").replace("🌹", "").strip().lower()}, escrito em português do século XVI.

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

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

        st.markdown(f"📜 **{titulo_poema}**")
        st.text(poema)
        st.markdown(f"*epopeIA — {data_hora}*")

        with st.spinner("🎧 A gerar voz..."):
            audio_path = gTTS(poema, lang="pt", tld="pt").save("poema.mp3")
            st.audio("poema.mp3", format="audio/mp3")
            with open("poema.mp3", "rb") as f:
                st.download_button("⬇️ Descarregar áudio", f, file_name="camoes_poema.mp3")

        # Botão para descarregar poema em texto
        caminho_txt = "poema.txt"
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(f"{titulo_poema}\n\n{poema}\n\nepopeIA — {data_hora}")
        
        with open(caminho_txt, "rb") as f:
            st.download_button("📜 Descarregar poema em texto", f, file_name="poema.txt", mime="text/plain")
