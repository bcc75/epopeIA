import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from openai import OpenAI
import os
import tempfile
import torch
import requests

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EpopeIA", page_icon="🌊")
st.title("🌊 EpopeIA — Ver com a Alma")

# --- CHAVES DE API ---
openai_key = os.getenv("OPENAI_API_KEY")
hf_token = os.getenv("HF_TOKEN")

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

# --- GERAR VOZ COM HUGGING FACE ---
def gerar_audio_huggingface(texto):
    api_url = "https://api-inference.huggingface.co/models/flax-community/vits-pt-cv-ft"
    headers = {
        "Authorization": f"Bearer {hf_token}"
    }
    payload = {
        "inputs": texto
    }
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        st.warning("⚠️ Erro ao gerar voz com Hugging Face.")
        return None

# --- INTERFACE ---
uploaded_file = st.file_uploader("📷 Carrega uma imagem", type=["jpg", "jpeg", "png"])
if uploaded_file and openai_key:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem carregada", use_container_width=True)

    with st.spinner("🔍 A interpretar a imagem..."):
        descricao = gerar_descricao(image)
        st.success(f"🧠 Descrição gerada: *{descricao}*")

    prompt = f"""Transforma a seguinte descrição numa poesia breve, bela e clássica, como se Camões a visse:

Descrição: {descricao}

Poema:"""

    with st.spinner("✍️ A escrever poesia com alma..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Escreves como um poeta clássico português, com tom elevado e influência camoniana."},
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

        # --- AUDIO HF ---
        with st.spinner("🎙️ A declamar com voz..."):
            audio = gerar_audio_huggingface(poema)
            if audio:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
                    fp.write(audio)
                    st.audio(fp.name, format="audio/wav")