import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from gtts import gTTS
import openai
import os
import tempfile
import torch

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="EpopeIA", page_icon="🌊")
st.title("🌊 EpopeIA — Ver com a Alma")

# --- CHAVE OPENAI ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ Erro: A chave da OpenAI não está configurada nos Secrets do Streamlit.")
else:
    openai.api_key = api_key

# --- CARREGAR BLIP ---
@st.cache_resource(show_spinner=False)
def load_blip():
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to("cuda" if torch.cuda.is_available() else "cpu")
    return processor, model

processor, model = load_blip()

# --- FUNÇÃO: DESCREVER IMAGEM ---
def gerar_descricao(imagem):
    inputs = processor(imagem, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        out = model.generate(**inputs)
    descricao = processor.decode(out[0], skip_special_tokens=True)
    return descricao

# --- UPLOAD DE IMAGEM ---
uploaded_file = st.file_uploader("📷 Carrega uma imagem", type=["jpg", "jpeg", "png"])
if uploaded_file and api_key:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem carregada", use_column_width=True)

    st.markdown("🔍 A interpretar a imagem com IA...")

    try:
        # Gerar descrição
        descricao = gerar_descricao(image)
        st.success(f"🧠 Descrição gerada: *{descricao}*")

        # --- GERA POEMA ---
        prompt = f"""Transforma a seguinte descrição numa poesia breve, bela e clássica, como se Camões a visse:

Descrição: {descricao}

Poema:"""

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=150
        )
        poema = response.choices[0].text.strip()
      st.markdown(f"""📝 **Poema:**  

> {poema.replace("\n", "\n> ")}  
""")
        # --- VOZ COM GTTS ---
        st.markdown("🔊 A gerar voz...")
        tts = gTTS(poema, lang='pt')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            st.audio(fp.name, format="audio/mp3")

    except Exception as e:
        st.error(f"❌ Erro ao processar a imagem: {e}")
