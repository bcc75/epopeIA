import streamlit as st
from PIL import Image
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

# Estilo visual
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://raw.githubusercontent.com/bcc75/epopeIA/main/fundep.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    section[data-testid="stRadio"] label span {
        font-size: 1.2rem !important;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<h1 style="font-size: 2.8rem; font-family: Arial, sans-serif; margin-bottom: 1.5rem; text-align: center;">
  <img src="https://raw.githubusercontent.com/bcc75/epopeIA/main/icon-lcamoes.png" style="height: 42px; vertical-align: middle; margin-right: 12px;">
  Epope<i>IA</i> — Ver com a Alma
</h1>
<div style="font-size: 1.3rem; font-family: Arial, sans-serif; line-height: 1.7; margin-bottom: 2rem; text-align: center;">
  <p><strong>Transformar imagens em poesia camoniana com a Inteligência Artificial</strong></p>
</div>
  <hr style="height:2px;border-width:0;color:gray;background-color:gray">
<div style="font-size: 1.1rem; font-family: Arial, sans-serif; line-height: 1.7; margin-bottom: 2rem;">
  <p> 📸  <strong>  Explora:</strong> a essência da imagem e deixa que a inteligência artificial a interprete e descreva.</p>
  <p> ✍️  <strong>  Descobre:</strong> a poesia escondida em cada imagem, sob o olhar de <em>Camões</em>.</p>
  <p> 📜  <strong>  Cria:</strong> novos mundos de imagens e palavras, onde a memória guia e o sonho avança.</p>
  <p> ⛵️  <strong>  Navega:</strong> entre <i>pixels</i> e versos, com a alma lusa sempre ao leme.</p>
    <hr style="height:2px;border-width:0;color:gray;background-color:gray">
</div>""", unsafe_allow_html=True)

def carregar_base(tom):
    caminho = "camoes_epico.txt" if tom == "⚔️ Épico" else "camoes_lirico.txt"
    with open(caminho, "r", encoding="utf-8") as f:
        versos = f.read().strip().split("EXEMPLO")
    return random.sample(versos, min(3, len(versos)))

openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key) if openai_key else None

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

def traduzir_descricao(desc):
    if not desc: return ""
    traducao = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Traduz esta descrição para português de Portugal, de forma natural e literária."},
            {"role": "user", "content": desc}
        ],
        temperature=0.3
    )
    return traducao.choices[0].message.content.strip()

def gerar_titulo_poema(descricao):
    prompt_titulo = f"Cria um título épico e poético, ao estilo de Camões, para um poema baseado nesta descrição: {descricao}"
    resposta_titulo = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Gera um título curto, épico e poético."},
            {"role": "user", "content": prompt_titulo}
        ],
        temperature=0.7,
        max_tokens=40
    )
    return resposta_titulo.choices[0].message.content.strip()

def gerar_audio_gtts(texto):
    tts = gTTS(texto, lang="pt", tld="pt")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
        tts.save(out.name)
        return out.name

uploaded_file = st.file_uploader("📷 Carrega uma imagem (JPG/PNG, até 200MB)", type=["jpg", "jpeg", "png"])
st.caption("📲 No iOS, o áudio pode requerer clique manual. A câmara nem sempre é ativada por segurança do browser.")
tom = st.radio(" 🎭 Escolhe o tom do poema:", ["⚔️ Épico", "🌹 Lírico"], index=1)

if uploaded_file and client:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem carregada", use_container_width=True)

    with st.spinner("🧬 A interpretar a imagem..."):
        desc_en = gerar_descricao(image)
        desc_pt = traduzir_descricao(desc_en)
        st.success(f"Descrição: *{desc_pt}*")

    titulo_poema = gerar_titulo_poema(desc_pt)
    exemplos = "\n\n".join(carregar_base(tom))

    prompt = f"""Transforma a seguinte descrição visual num poema escrito por Luís de Camões, respeitando rigorosamente a métrica, a forma e o estilo da sua poesia clássica.
Se for **épico**, escreve apenas uma oitava real, ou seja, 8 versos decassilábicos com rima ABABABCC, isto é, devem ter rima cruzada nos seis primeiros e emparelhada nos dois últimos. Deves escrever apenas uma única oitava, sem mais estrofes, evocando feitos gloriosos, viagens, o mar, a pátria, o engenho humano e a mitologia clássica. O tom deve ser solene, grandioso e heroico, com linguagem elevada e cadência narrativa inspirada em *Os Lusíadas*.
Se for **lírico**, escreve um **soneto clássico italiano** (14 versos organizados em 4 estrofes fixas com 2 quartetos e 2 tercetos) com rima ABBA ABBA CDC DCD, explorando sentimentos como amor idealizado, saudade, abandono, sofrimento e a impossibilidade da felicidade amorosa. Dá ênfase à tensão entre o desejo e a razão, à beleza da mulher inatingível, ao prazer e à dor que o amor provoca.
A linguagem deve ser em português do século XVI, rica em metáforas, inversões sintáticas e musicalidade.
Inspira-te nestes exemplos camonianos:

{exemplos}

Descrição da imagem:
{desc_pt}

Poema:"""

    with st.spinner("✍️ A gerar poema camoniano..."):
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Escreve como Luís de Camões, respeitando forma, métrica e estilo do século XVI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        poema = resposta.choices[0].message.content.strip()
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

        st.markdown(f"📜 **{titulo_poema}**")
        st.text(poema)
        st.markdown(f"*epopeIA — {data_hora}*")

        with st.spinner("🗣️ A gerar voz..."):
            audio_path = gerar_audio_gtts(poema)
            st.audio(audio_path, format="audio/mp3")
            with open(audio_path, "rb") as f:
                st.download_button("🎧 Descarregar áudio", f, file_name="camoes_poema.mp3")

        caminho_txt = "poema.txt"
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(f"{titulo_poema}\n\n{poema}\n\nepopeIA — {data_hora}")
        with open(caminho_txt, "rb") as f:
            st.download_button("📜 Descarregar poema em texto", f, file_name="poema.txt", mime="text/plain")
