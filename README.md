readme_path = "/mnt/data/README.md"

conteudo_readme = """
# 🌊 EpopeIA — Ver com a Alma

**EpopeIA** é uma aplicação poético-assistiva que transforma imagens em poesia inspirada na obra de Luís de Camões. Utiliza Inteligência Artificial para descrever visualmente uma imagem e recriar, com linguagem clássica e vocabulário do século XVI, um poema inédito.

---

## 📸 Funcionalidades

- Carregamento de imagens (JPG/PNG)
- Interpretação automática com IA (modelo BLIP via Hugging Face)
- Geração de poemas com base em *Os Lusíadas*, sonetos e redondilhas de Camões
- Escolha entre dois estilos:
  - ⚔️ **Épico** — inspirado na epopeia marítima e heroica
  - 🌹 **Romântico** — inspirado nos versos líricos e amorosos
- Leitura em voz alta com **voz masculina portuguesa** (Google Cloud Text-to-Speech)
- Opção de descarregar o poema em áudio

---

## 🚀 Como executar no Streamlit Cloud

1. Faz fork ou upload deste repositório para o teu GitHub.
2. Vai a [https://share.streamlit.io](https://share.streamlit.io) e cria uma nova app.
3. Escolhe o repositório e define `epopeia_app.py` como ficheiro principal.
4. Nas definições da app, adiciona as tuas credenciais em **Secrets**:

```toml
OPENAI_API_KEY = "a_tua_chave_openai"
GOOGLE_TTS_API_KEY = "a_tua_chave_google"
