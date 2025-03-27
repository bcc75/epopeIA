
# EpopeIA — Ver com a Alma
# Código corrigido com fonte maior no radio button

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

# Adicionar CSS personalizado
st.markdown("""
    <style>
        body {
            background-image: url('https://raw.githubusercontent.com/bcc75/epopeIA/main/fundo.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        div[class*='stRadio'] label {
            font-size: 1.3rem !important;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""<h1 style="font-size: 2rem; font-family: Helvetica, sans-serif; margin-bottom: 1.5rem;">
  <img src="https://raw.githubusercontent.com/bcc75/epopeIA/main/lcamoes2.jpeg" style="height: 42px; vertical-align: middle; margin-right: 12px;">
  EpopeIA — Ver com a Alma
</h1>

<div style="font-size: 1.1rem; font-family: Helvetica, sans-serif; line-height: 1.7; margin-bottom: 2rem;">
  <p>📸 <strong>Vê com os olhos:</strong> carrega uma imagem e deixa que a inteligência artificial a interprete.</p>
  <p>✍️ <strong>Ouve com a alma:</strong> a descrição torna-se um poema ao estilo de <em>Camões</em>.</p>
  <p>📜 <strong>Poesia assistiva:</strong> uma ponte entre a visão e a palavra, entre o passado e o futuro.</p>
  <p>⛵ <strong>EpopeIA:</strong> navega entre pixels e versos, com a alma lusitana sempre ao leme.</p>
</div>""", unsafe_allow_html=True)
