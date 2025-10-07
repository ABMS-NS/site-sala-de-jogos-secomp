import streamlit as st
import requests
import json
import base64
from datetime import datetime

# Importar configurações do arquivo config.py
from config import GITHUB_TOKEN, GITHUB_REPO, GITHUB_FILE


def get_github_data():
    """Busca dados do arquivo JSON no GitHub"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return {"players": {}}, None
        
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            decoded_content = base64.b64decode(content['content']).decode('utf-8')
            return json.loads(decoded_content), content['sha']
        elif response.status_code == 404:
            st.warning("⚠️ Arquivo leaderboard.json não encontrado no GitHub. Será criado ao salvar dados.")
            return {"players": {}}, None
        else:
            st.error(f"❌ Erro ao buscar dados: {response.status_code}")
            return {"players": {}}, None
    except Exception as e:
        st.error(f"❌ Erro na conexão com GitHub: {str(e)}")
        return {"players": {}}, None


def save_github_data(data, sha=None):
    """Salva dados no arquivo JSON do GitHub"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        st.error("⚠️ Credenciais do GitHub não configuradas")
        return False
        
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    content_encoded = base64.b64encode(json.dumps(data, indent=4, ensure_ascii=False).encode()).decode()
    
    payload = {
        "message": f"Update leaderboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "content": content_encoded
    }
    
    if sha:
        payload["sha"] = sha
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"❌ Erro ao salvar: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Erro ao salvar: {str(e)}")
        return False