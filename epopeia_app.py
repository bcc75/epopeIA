import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from openai import OpenAI
from elevenlabs import generate, play, save, set_api_key
import os
import tempfile
import torch

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EpopeIA", page_icon="🌊")
st.title("🌊 EpopeIA — Ver com a Alma")

# --- CHAVES DE API ---
openai_key = os.getenv("OPENAI_API_KEY")
eleven_key = os.getenv("ELEVEN_API_KEY")
voice_id = os.getenv("ELEVEN_VOICE_ID")

if not openai_key:
    st.error("❌ Erro: A chave da OpenAI não está configurada.")
else:
    client = OpenAI(api_key=openai_key)

# --- INICIAR ElevenLabs ---
if eleven_key:
    set_api_key(eleven_key)
else:
    st.warning("⚠️ A voz do Camões está sem API Key da ElevenLabs.")

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

        if eleven_key and voice_id:
            with st.spinner("🎙️ A dar voz ao poema..."):
                audio = generate(text=poema, voice=voice_id, model="eleven_multilingual_v2")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    save(audio, fp.name)
                    st.audio(fp.name, format="audio/mp3")
        else:
            st.info("ℹ️ Voz não disponível. Verifica a chave ou o ID da voz.")