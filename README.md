# EpopeIA 🌊📜

Uma aplicação assistiva e poética baseada em IA, inspirada nos 500 anos de Luís de Camões.

## Funcionalidades
- **Interpretação automática de imagens** com **BLIP do Hugging Face**
- **Geração de poesia em estilo camoniano** com OpenAI
- **Leitura do poema com voz PT-PT** via gTTS (Google Text-to-Speech)

## Como correr no Streamlit Cloud

1. **Adiciona as chaves no Streamlit Cloud** em **Settings > Secrets**:

```
OPENAI_API_KEY="sk-..."
```

2. **Faz deploy no Streamlit Cloud**
   - Sobe os ficheiros para o GitHub
   - Liga o repositório ao [Streamlit Cloud](https://share.streamlit.io/)
   - Define `epopeia_app.py` como ficheiro principal

3. **Executa e partilha!**