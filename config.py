import streamlit as st
import os
from dotenv import load_dotenv

# Tentar carregar do Streamlit Secrets primeiro, senão do .env
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    GITHUB_REPO = st.secrets["GITHUB_REPO"]
    GITHUB_FILE = st.secrets["GITHUB_FILE"]
    ADMIN_CREDENTIALS = dict(st.secrets.get("ADMINS", {}))
except:
    st.error("⚠️ Erro ao carregar as Secrets do Streamlit Cloud. Verifique se estão configuradas corretamente.")
# Aviso se as credenciais não estiverem configuradas
if not GITHUB_TOKEN or not GITHUB_REPO:
    st.error("⚠️ Configure as variáveis GITHUB_TOKEN e GITHUB_REPO no arquivo .env ou nas Secrets do Streamlit Cloud")