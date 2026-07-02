import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from openai import (
    OpenAI,
    RateLimitError,
    APIError,
    APITimeoutError,
    APIConnectionError
)
from gtts import gTTS
import os
import tempfile
import torch
import random
import time
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


def obter_config(nome, valor_padrao=None):
    """
    Vai buscar uma configuração ao Streamlit Secrets ou às variáveis de ambiente.
    Evita erro quando não existe ficheiro secrets.toml em ambiente local.
    """
    try:
        return st.secrets.get(nome, os.getenv(nome, valor_padrao))
    except Exception:
        return os.getenv(nome, valor_padrao)


def carregar_base(tom):
    caminho = "camoes_epico.txt" if tom == "⚔️ Épico" else "camoes_lirico.txt"

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            versos = f.read().strip().split("EXEMPLO")
        return random.sample(versos, min(3, len(versos)))
    except FileNotFoundError:
        return [
            "Exemplo camoniano indisponível. Mantém linguagem elevada, clássica, musical e poética."
        ]


openai_key = obter_config("OPENAI_API_KEY")
OPENAI_MODEL = obter_config("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=openai_key) if openai_key else None


@st.cache_resource(show_spinner=False)
def load_blip():
    device = "cuda" if torch.cuda.is_available() else "cpu"

    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )

    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    ).to(device)

    return processor, model, device


processor, model, device = load_blip()


def gerar_descricao(imagem):
    inputs = processor(imagem, return_tensors="pt").to(device)

    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=50)

    return processor.decode(out[0], skip_special_tokens=True)


def chamar_openai_chat(
    messages,
    temperature=0.7,
    max_tokens=300,
    fallback="",
    tentativas=2
):
    """
    Chamada segura à OpenAI.
    Mostra o erro real no Streamlit para facilitar diagnóstico.
    """

    if client is None:
        st.error("⚠️ Cliente OpenAI não inicializado. Verifica a OPENAI_API_KEY.")
        return fallback

    ultimo_erro = None

    for tentativa in range(tentativas):
        try:
            resposta = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            conteudo = resposta.choices[0].message.content

            if conteudo:
                return conteudo.strip()

            st.warning("A OpenAI respondeu, mas não devolveu conteúdo.")
            return fallback

        except RateLimitError as e:
            ultimo_erro = e

            if tentativa < tentativas - 1:
                espera = (2 ** (tentativa + 1)) + random.uniform(0, 1)
                time.sleep(espera)
                continue

            st.error("⚠️ Limite/quota da API OpenAI atingido.")
            st.code(str(e))
            return fallback

        except (APITimeoutError, APIConnectionError, APIError) as e:
            ultimo_erro = e

            if tentativa < tentativas - 1:
                espera = (2 ** (tentativa + 1)) + random.uniform(0, 1)
                time.sleep(espera)
                continue

            st.error("⚠️ Erro temporário de ligação ou resposta da API OpenAI.")
            st.code(str(e))
            return fallback

        except Exception as e:
            ultimo_erro = e
            st.error("⚠️ Erro inesperado na chamada à OpenAI.")
            st.code(str(e))
            return fallback

    if ultimo_erro:
        st.code(str(ultimo_erro))

    return fallback

        except RateLimitError:
            # Espera progressiva: 2s, 4s, 8s, com pequeno fator aleatório
            if tentativa < tentativas - 1:
                espera = (2 ** (tentativa + 1)) + random.uniform(0, 1)
                time.sleep(espera)
                continue

            return fallback

        except (APITimeoutError, APIConnectionError, APIError):
            if tentativa < tentativas - 1:
                espera = (2 ** (tentativa + 1)) + random.uniform(0, 1)
                time.sleep(espera)
                continue

            return fallback

        except Exception:
            return fallback

    return fallback


@st.cache_data(show_spinner=False, ttl=86400)
def traduzir_descricao(desc):
    """
    Traduz a descrição gerada pelo BLIP.
    Fica em cache durante 24 horas para evitar chamadas repetidas à OpenAI.
    """

    if not desc or not desc.strip():
        return "imagem sem descrição disponível"

    desc = desc.strip()

    messages = [
        {
            "role": "system",
            "content": (
                "Traduz descrições de imagem para português europeu, "
                "de forma natural, clara e ligeiramente literária. "
                "Não acrescentes comentários."
            )
        },
        {
            "role": "user",
            "content": desc
        }
    ]

    return chamar_openai_chat(
        messages=messages,
        temperature=0.3,
        max_tokens=120,
        fallback=desc,
        tentativas=3
    )


@st.cache_data(show_spinner=False, ttl=86400)
def gerar_titulo_poema(descricao):
    """
    Gera um título curto.
    Também fica em cache para evitar repetir chamadas desnecessárias.
    """

    if not descricao:
        return "Ver com a Alma"

    prompt_titulo = (
        "Cria um título curto, épico e poético, ao estilo de Camões, "
        f"para um poema baseado nesta descrição: {descricao}"
    )

    messages = [
        {
            "role": "system",
            "content": "Gera apenas um título curto, épico e poético. Não uses aspas."
        },
        {
            "role": "user",
            "content": prompt_titulo
        }
    ]

    return chamar_openai_chat(
        messages=messages,
        temperature=0.7,
        max_tokens=40,
        fallback="Ver com a Alma",
        tentativas=3
    )


def gerar_poema_camoniano(desc_pt, exemplos, tom):
    prompt = f"""Transforma a seguinte descrição visual num poema escrito por Luís de Camões, respeitando rigorosamente a métrica, a forma e o estilo da sua poesia clássica.

Tom escolhido:
{tom}

Se for **épico**, escreve apenas uma oitava real, ou seja, 8 versos decassilábicos com rima ABABABCC, isto é, devem ter rima cruzada nos seis primeiros e emparelhada nos dois últimos. Deves escrever apenas uma única oitava, sem mais estrofes, evocando feitos gloriosos, viagens, o mar, a pátria, o engenho humano e a mitologia clássica. O tom deve ser solene, grandioso e heroico, com linguagem elevada e cadência narrativa inspirada em Os Lusíadas.

Se for **lírico**, escreve um soneto clássico italiano com 14 versos organizados em 4 estrofes fixas com 2 quartetos e 2 tercetos, com rima ABBA ABBA CDC DCD, explorando sentimentos como amor idealizado, saudade, abandono, sofrimento e a impossibilidade da felicidade amorosa. Dá ênfase à tensão entre o desejo e a razão, à beleza da mulher inatingível, ao prazer e à dor que o amor provoca.

A linguagem deve ser em português europeu, rica em metáforas, inversões sintáticas e musicalidade.

Inspira-te nestes exemplos camonianos:

{exemplos}

Descrição da imagem:
{desc_pt}

Poema:"""

    messages = [
        {
            "role": "system",
            "content": (
                "Escreve como Luís de Camões, respeitando forma, métrica, "
                "musicalidade e estilo clássico do século XVI. "
                "Devolve apenas o poema."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    poema_fallback = (
        "Não foi possível gerar o poema neste momento, "
        "por limite temporário da API. Tenta novamente dentro de instantes."
    )

    return chamar_openai_chat(
        messages=messages,
        temperature=0.7,
        max_tokens=500,
        fallback=poema_fallback,
        tentativas=3
    )


def gerar_audio_gtts_bytes(texto):
    """
    Gera áudio com gTTS e devolve bytes.
    Assim evita depender de caminhos temporários após reruns do Streamlit.
    """

    try:
        tts = gTTS(texto, lang="pt", tld="pt")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
            caminho_temp = out.name

        tts.save(caminho_temp)

        with open(caminho_temp, "rb") as f:
            audio_bytes = f.read()

        os.remove(caminho_temp)

        return audio_bytes

    except Exception:
        return None


uploaded_file = st.file_uploader(
    "📷 Carrega uma imagem (JPG/PNG, até 200MB)",
    type=["jpg", "jpeg", "png"]
)

st.caption(
    "📲 No iOS, o áudio pode requerer clique manual. "
    "A câmara nem sempre é ativada por segurança do browser."
)

tom = st.radio(
    " 🎭 Escolhe o tom do poema:",
    ["⚔️ Épico", "🌹 Lírico"],
    index=1
)


if client is None:
    st.error(
        "⚠️ A chave OPENAI_API_KEY não foi encontrada. "
        "Configura-a nos Secrets do Streamlit Cloud ou nas variáveis de ambiente."
    )


if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem carregada", use_container_width=True)

    gerar = st.button("✨ Gerar poema camoniano", type="primary")

    if gerar and client:
        with st.spinner("🧬 A interpretar a imagem..."):
            desc_en = gerar_descricao(image)
            desc_pt = traduzir_descricao(desc_en)

        if desc_pt == desc_en:
            st.info(
                "A tradução automática não ficou disponível neste momento. "
                "A app vai continuar com a descrição original."
            )

        with st.spinner("✍️ A gerar poema camoniano..."):
            titulo_poema = gerar_titulo_poema(desc_pt)
            exemplos = "\n\n".join(carregar_base(tom))
            poema = gerar_poema_camoniano(desc_pt, exemplos, tom)
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

        with st.spinner("🗣️ A gerar voz..."):
            audio_bytes = gerar_audio_gtts_bytes(poema)

        st.session_state["resultado_epopeia"] = {
            "desc_pt": desc_pt,
            "titulo_poema": titulo_poema,
            "poema": poema,
            "data_hora": data_hora,
            "audio_bytes": audio_bytes
        }


if "resultado_epopeia" in st.session_state:
    resultado = st.session_state["resultado_epopeia"]

    st.success(f"Descrição: *{resultado['desc_pt']}*")

    st.markdown(f"📜 **{resultado['titulo_poema']}**")
    st.text(resultado["poema"])
    st.markdown(f"*epopeIA — {resultado['data_hora']}*")

    if resultado["audio_bytes"]:
        st.audio(resultado["audio_bytes"], format="audio/mp3")
        st.download_button(
            "🎧 Descarregar áudio",
            resultado["audio_bytes"],
            file_name="camoes_poema.mp3",
            mime="audio/mp3"
        )
    else:
        st.warning("Não foi possível gerar o áudio neste momento.")

    texto_poema = (
        f"{resultado['titulo_poema']}\n\n"
        f"{resultado['poema']}\n\n"
        f"epopeIA — {resultado['data_hora']}"
    )

    st.download_button(
        "📜 Descarregar poema em texto",
        texto_poema.encode("utf-8"),
        file_name="poema.txt",
        mime="text/plain"
    )
