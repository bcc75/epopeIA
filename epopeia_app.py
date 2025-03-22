import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from openai import OpenAI
from gtts import gTTS
import os
import tempfile
import torch

# --- CONFIGURAÇÃO ---
st.set_page_config(
    page_title="EpopeIA",
    page_icon="https://github.com/bcc75/epopeIA/blob/main/lcamoes2.jpeg"
)

st.markdown("""
<div style="display: flex; align-items: center;">
    <img src="https://github.com/bcc75/epopeIA/blob/main/lcamoes2.jpeg" width="40" style="margin-right: 10px">
    <h1 style='display: inline; font-size: 32px;'>EpopeIA — Ver com a Alma</h1>
</div>
""", unsafe_allow_html=True)

# --- CHAVE DA OPENAI ---
openai_key = os.getenv("OPENAI_API_KEY")

if not openai_key:
    st.error("❌ Erro: A chave da OpenAI não está configurada.")
else:
    client = OpenAI(api_key=openai_key)

# --- CARREGAR BLIP ---
@st.cache_resource(show_spinner=False)
def load_blip():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to("cuda" if torch.cuda.is_available() else "cpu")
    return processor, model

processor, model = load_blip()

# --- DESCREVER IMAGEM ---
def gerar_descricao(imagem):
    inputs = processor(imagem, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

# --- GERAR VOZ COM gTTS ---
def gerar_audio(poema):
    tts = gTTS(text=poema, lang='pt', tld='pt')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

# --- INTERFACE ---
uploaded_file = st.file_uploader(
    "📷  Seleciona ou arrasta uma imagem (JPG/PNG, até 200MB)",
    type=["jpg", "jpeg", "png"],
    label_visibility="visible"
)
st.caption("-> Se aparecer 'Browse files', isso depende da linguagem do navegador.")

if uploaded_file and openai_key:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem carregada", use_container_width=True)

    with st.spinner("🔍 A interpretar a imagem..."):
        descricao = gerar_descricao(image)
        st.success(f"🧠 Descrição gerada: *{descricao}*")

    prompt = f"""Imagina que és Luís de Camões e olhas esta cena com olhos de poeta do século XVI.
Transfigura a seguinte descrição num poema breve, com alma épica, linguagem clássica, metáforas náuticas e elevação poética.
Usa vocabulário do século XVI e estruturas próprias da poesia portuguesa renascentista.

Descrição: {descricao}

Poema:"""

    with st.spinner("✍️ A escrever poesia com alma..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Escreves como Luís de Camões. Usa vocabulário do século XVI, estrutura poética clássica portuguesa, metáforas náuticas, e um tom épico e elevado. Podes usar inversões sintácticas e construções arcaicas, mas mantém clareza."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        poema = response.choices[0].message.content.strip()
        st.markdown(f"""
        📝 **Poema:**  

        > {poema.replace("\n", "\n> ")}
        """)

        with st.spinner("🎙️ A gerar voz..."):
            audio_path = gerar_audio(poema)
            st.audio(audio_path, format="audio/mp3")
