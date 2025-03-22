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
    page_icon="https://raw.githubusercontent.com/bcc75/epopeIA/main/lcamoes2.jpeg"
)

st.markdown("""
<div style="display: flex; align-items: center;">
    <img src="https://raw.githubusercontent.com/bcc75/epopeIA/main/lcamoes2.jpeg" width="40" style="margin-right: 10px">
    <h1 style='display: inline; font-size: 32px;'>EpopeIA — Ver com a Alma</h1>
</div>
<p style="font-size: 18px; margin-top: -10px; line-height: 1.6;">
    <span style="font-size: 20px;">📸</span> <strong>Vê com os olhos</strong> — carrega uma imagem e deixa que a inteligência artificial a interprete.<br>
    <span style="font-size: 20px;">✍️</span> <strong>Ouve com a alma</strong> — a descrição torna-se um poema ao estilo de <em>Camões</em>.<br>
    <span style="font-size: 20px;">📜</span> <strong>Poesia assistiva</strong> — uma ponte entre a visão e a palavra, entre o passado e o futuro.<br>
    <span style="font-size: 20px;">⛵</span> <strong>EpopeIA</strong> navega entre pixels e versos, com a alma lusitana sempre ao leme.
</p>
""", unsafe_allow_html=True)

# --- LER EXCERTOS CAMONIANOS ---
with open("camoes.txt", "r", encoding="utf-8") as f:
    estilo_camoes = f.read().strip()

# --- OPENAI ---
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    st.error("❌ Erro: Chave da OpenAI não encontrada.")
else:
    client = OpenAI(api_key=openai_key)

# --- BLIP ---
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

def gerar_audio(poema):
    tts = gTTS(text=poema, lang='pt', tld='pt')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name

# --- INTERFACE ---
uploaded_file = st.file_uploader("📷 Carrega uma imagem (JPG/PNG, até 200MB)", type=["jpg", "jpeg", "png"])
st.caption("🛈 No iOS, o áudio pode requerer clique manual. A câmara nem sempre é ativada por segurança do browser.")

# Escolha do tom poético
tom = st.radio("🎭 Escolhe o tom do poema:", ["⚔️ Épico", "🌹 Romântico"])

if uploaded_file and openai_key:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem carregada", use_container_width=True)

    with st.spinner("🧠 A interpretar a imagem..."):
        descricao = gerar_descricao(image)
        st.success(f"Descrição: *{descricao}*")

    estilo = "épico e clássico, com vocabulário do século XVI e estrutura lírica portuguesa" if "Épico" in tom else "romântico, melancólico e introspectivo, com vocabulário clássico e doçura emocional"

    prompt = f"""
Tu és Luís de Camões. A tua missão é transformar uma descrição visual num poema com tom {tom.replace("⚔️", "").replace("🌹", "").strip().lower()}, escrito em português do século XVI.

Inspira-te nestes exemplos do teu estilo:

{estilo_camoes}

Agora, escreve um poema {estilo} inspirado na seguinte descrição:
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
            max_tokens=300
        )
        poema = response.choices[0].message.content.strip()
        st.markdown(f"📝 **Poema ({tom}):**\n\n> {poema.replace('\n', '\n> ')}")

        with st.spinner("🎧 A gerar voz..."):
            audio_path = gerar_audio(poema)
            st.audio(audio_path, format="audio/mp3")
            with open(audio_path, "rb") as f:
                st.download_button("⬇️ Descarregar áudio", f, file_name="camoes_poema.mp3")