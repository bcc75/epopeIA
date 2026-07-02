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
import json
import hashlib
from datetime import datetime


# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================

st.set_page_config(
    page_title="EpopeIA",
    page_icon="https://raw.githubusercontent.com/bcc75/epopeIA/main/lcamoes2.jpeg"
)


# =========================
# ESTILO VISUAL
# =========================

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

st.markdown(
    """
<h1 style="font-size: 2.8rem; font-family: Arial, sans-serif; margin-bottom: 1.5rem; text-align: center;">
  <img src="https://raw.githubusercontent.com/bcc75/epopeIA/main/icon-lcamoes.png" style="height: 42px; vertical-align: middle; margin-right: 12px;">
  Epope<i>IA</i> — Ver com a Alma
</h1>
<div style="font-size: 1.3rem; font-family: Arial, sans-serif; line-height: 1.7; margin-bottom: 2rem; text-align: center;">
  <p><strong>Transformar imagens em poesia camoniana com a Inteligência Artificial</strong></p>
</div>
<hr style="height:2px;border-width:0;color:gray;background-color:gray">
<div style="font-size: 1.1rem; font-family: Arial, sans-serif; line-height: 1.7; margin-bottom: 2rem;">
  <p>📸 <strong>Explora:</strong> a essência da imagem e deixa que a inteligência artificial a interprete e descreva.</p>
  <p>✍️ <strong>Descobre:</strong> a poesia escondida em cada imagem, sob o olhar de <em>Camões</em>.</p>
  <p>📜 <strong>Cria:</strong> novos mundos de imagens e palavras, onde a memória guia e o sonho avança.</p>
  <p>⛵️ <strong>Navega:</strong> entre <i>pixels</i> e versos, com a alma lusa sempre ao leme.</p>
  <hr style="height:2px;border-width:0;color:gray;background-color:gray">
</div>
    """,
    unsafe_allow_html=True
)


# =========================
# CONFIGURAÇÕES E CLIENTES
# =========================

def obter_config(nome, valor_padrao=None):
    """
    Obtém valores a partir dos Secrets do Streamlit Cloud ou das variáveis de ambiente.
    """
    try:
        valor = st.secrets.get(nome, None)
    except Exception:
        valor = None

    if valor is None:
        valor = os.getenv(nome, valor_padrao)

    if isinstance(valor, str):
        valor = valor.strip()

    return valor


openai_key = obter_config("OPENAI_API_KEY")
OPENAI_MODEL = obter_config("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=openai_key) if openai_key else None


# =========================
# CARREGAMENTO DO MODELO BLIP
# =========================

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


# =========================
# FUNÇÕES AUXILIARES
# =========================

def calcular_hash_ficheiro(uploaded_file):
    """
    Cria uma assinatura única para a imagem carregada.
    Ajuda a evitar mostrar resultados antigos quando se troca de imagem.
    """
    dados = uploaded_file.getvalue()
    return hashlib.md5(dados).hexdigest()


def carregar_base(tom):
    """
    Carrega exemplos camonianos de acordo com o tom escolhido.
    """
    caminho = "camoes_epico.txt" if tom == "⚔️ Épico" else "camoes_lirico.txt"

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            versos = f.read().strip().split("EXEMPLO")

        versos = [v.strip() for v in versos if v.strip()]

        if not versos:
            return [
                "Mantém linguagem elevada, clássica, musical e poética, inspirada em Camões."
            ]

        return random.sample(versos, min(3, len(versos)))

    except FileNotFoundError:
        return [
            "Mantém linguagem elevada, clássica, musical e poética, inspirada em Camões."
        ]


def gerar_descricao(imagem):
    """
    Gera uma descrição visual em inglês com BLIP.
    """
    inputs = processor(imagem, return_tensors="pt").to(device)

    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=50)

    return processor.decode(out[0], skip_special_tokens=True).strip()


def mostrar_erro_openai(mensagem, erro):
    """
    Mostra erro técnico sem interromper a aplicação.
    """
    st.error(mensagem)

    erro_texto = str(erro)

    if erro_texto:
        st.code(erro_texto)


def chamar_openai_chat(
    messages,
    temperature=0.7,
    max_tokens=700,
    tentativas=2
):
    """
    Faz uma chamada segura à OpenAI com retry simples e exponential backoff.
    Devolve uma string ou None.
    """

    if client is None:
        st.error("⚠️ Cliente OpenAI não inicializado. Verifica a OPENAI_API_KEY.")
        return None

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

            if conteudo and conteudo.strip():
                return conteudo.strip()

            st.warning("A OpenAI respondeu, mas não devolveu conteúdo.")
            return None

        except RateLimitError as e:
            ultimo_erro = e

            if tentativa < tentativas - 1:
                espera = (2 ** (tentativa + 1)) + random.uniform(0, 1)
                time.sleep(espera)
                continue

            mostrar_erro_openai(
                "⚠️ Limite ou quota da API OpenAI atingido. Verifica o plano, os créditos, o orçamento mensal ou o limite do projeto.",
                e
            )
            return None

        except (APITimeoutError, APIConnectionError, APIError) as e:
            ultimo_erro = e

            if tentativa < tentativas - 1:
                espera = (2 ** (tentativa + 1)) + random.uniform(0, 1)
                time.sleep(espera)
                continue

            mostrar_erro_openai(
                "⚠️ Erro temporário de ligação ou resposta da API OpenAI.",
                e
            )
            return None

        except Exception as e:
            ultimo_erro = e
            mostrar_erro_openai(
                "⚠️ Erro inesperado na chamada à OpenAI.",
                e
            )
            return None

    if ultimo_erro:
        mostrar_erro_openai("⚠️ Erro na chamada à OpenAI.", ultimo_erro)

    return None


def limpar_json_resposta(texto):
    """
    Remove cercas Markdown e tenta extrair o primeiro objeto JSON válido da resposta.
    """
    if not texto:
        return None

    texto = texto.strip()

    if texto.startswith("```"):
        texto = texto.replace("```json", "").replace("```", "").strip()

    inicio = texto.find("{")
    fim = texto.rfind("}")

    if inicio == -1 or fim == -1 or fim <= inicio:
        return None

    candidato = texto[inicio:fim + 1]

    try:
        return json.loads(candidato)
    except json.JSONDecodeError:
        return None


def gerar_resultado_camoniano(desc_en, exemplos, tom):
    """
    Faz uma única chamada à OpenAI para:
    1. traduzir a descrição;
    2. gerar o título;
    3. gerar o poema.

    Isto reduz o número de pedidos à API e diminui o risco de RateLimitError.
    """

    exemplos_texto = "\n\n".join(exemplos)

    prompt = f"""
A partir da descrição visual abaixo, cria um resultado literário inspirado em Luís de Camões.

Descrição visual original, em inglês:
{desc_en}

Tom escolhido:
{tom}

Regras:
- Traduz a descrição para português europeu, de forma natural e ligeiramente literária.
- Cria um título curto, épico e poético.
- Se o tom escolhido for "⚔️ Épico", escreve apenas uma oitava real:
  - 8 versos;
  - tendência decassilábica;
  - rima ABABABCC;
  - tom solene, marítimo, heroico, grandioso e clássico.
- Se o tom escolhido for "🌹 Lírico", escreve um soneto clássico italiano:
  - 14 versos;
  - 2 quartetos e 2 tercetos;
  - rima aproximada ABBA ABBA CDC DCD;
  - tom amoroso, saudoso, contemplativo e musical.
- Usa português europeu.
- Usa metáforas, inversões sintáticas e vocabulário elevado.
- Não expliques o poema.
- Não escrevas notas finais.

Exemplos de inspiração camoniana:
{exemplos_texto}

Devolve apenas JSON válido, sem Markdown, exatamente com estas três chaves:
{{
  "descricao_pt": "...",
  "titulo": "...",
  "poema": "..."
}}
    """.strip()

    messages = [
        {
            "role": "system",
            "content": (
                "És um escritor literário especializado em Camões. "
                "Responde apenas com JSON válido. "
                "Não uses Markdown. Não uses comentários antes ou depois do JSON."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    texto = chamar_openai_chat(
        messages=messages,
        temperature=0.7,
        max_tokens=800,
        tentativas=2
    )

    dados = limpar_json_resposta(texto)

    if not dados:
        return {
            "descricao_pt": desc_en,
            "titulo": "Ver com a Alma",
            "poema": (
                "Não foi possível gerar o poema neste momento. "
                "Verifica a chave da OpenAI, o modelo configurado, a quota disponível "
                "ou os limites de utilização da API."
            )
        }

    descricao_pt = dados.get("descricao_pt", "").strip()
    titulo = dados.get("titulo", "").strip()
    poema = dados.get("poema", "").strip()

    if not descricao_pt:
        descricao_pt = desc_en

    if not titulo:
        titulo = "Ver com a Alma"

    if not poema:
        poema = (
            "Não foi possível gerar o poema neste momento. "
            "Verifica a chave da OpenAI, o modelo configurado, a quota disponível "
            "ou os limites de utilização da API."
        )

    return {
        "descricao_pt": descricao_pt,
        "titulo": titulo,
        "poema": poema
    }


def gerar_audio_gtts_bytes(texto):
    """
    Gera áudio com gTTS e devolve bytes.
    """
    if not texto or not texto.strip():
        return None

    try:
        tts = gTTS(texto, lang="pt", tld="pt")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
            caminho_temp = out.name

        tts.save(caminho_temp)

        with open(caminho_temp, "rb") as f:
            audio_bytes = f.read()

        os.remove(caminho_temp)

        return audio_bytes

    except Exception as e:
        st.warning("Não foi possível gerar o áudio neste momento.")
        st.code(str(e))
        return None


# =========================
# INTERFACE
# =========================

uploaded_file = st.file_uploader(
    "📷 Carrega uma imagem (JPG/PNG, até 200MB)",
    type=["jpg", "jpeg", "png"]
)

st.caption(
    "📲 No iOS, o áudio pode requerer clique manual. "
    "A câmara nem sempre é ativada por segurança do browser."
)

tom = st.radio(
    "🎭 Escolhe o tom do poema:",
    ["⚔️ Épico", "🌹 Lírico"],
    index=1
)

with st.sidebar:
    st.markdown("### ⚙️ Configuração")
    st.caption(f"Modelo OpenAI: `{OPENAI_MODEL}`")

    if client is None:
        st.error("OPENAI_API_KEY não encontrada.")
    else:
        st.success("OPENAI_API_KEY carregada.")


if client is None:
    st.error(
        "⚠️ A chave OPENAI_API_KEY não foi encontrada. "
        "Configura-a nos Secrets do Streamlit Cloud ou nas variáveis de ambiente."
    )


if uploaded_file:
    imagem_hash = calcular_hash_ficheiro(uploaded_file)
    chave_atual = f"{imagem_hash}_{tom}"

    if st.session_state.get("chave_resultado") != chave_atual:
        st.session_state.pop("resultado_epopeia", None)

    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagem carregada", use_container_width=True)

    gerar = st.button("✨ Gerar poema camoniano", type="primary")

    if gerar and client:
        with st.spinner("🧬 A interpretar a imagem..."):
            desc_en = gerar_descricao(image)

        with st.spinner("✍️ A gerar descrição, título e poema camoniano..."):
            exemplos = carregar_base(tom)
            resultado_openai = gerar_resultado_camoniano(desc_en, exemplos, tom)
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

        with st.spinner("🗣️ A gerar voz..."):
            audio_bytes = gerar_audio_gtts_bytes(resultado_openai["poema"])

        st.session_state["chave_resultado"] = chave_atual
        st.session_state["resultado_epopeia"] = {
            "desc_en": desc_en,
            "desc_pt": resultado_openai["descricao_pt"],
            "titulo_poema": resultado_openai["titulo"],
            "poema": resultado_openai["poema"],
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
        st.warning("Não foi possível gerar o áudio deste poema.")

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
