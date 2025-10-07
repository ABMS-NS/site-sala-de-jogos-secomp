import streamlit as st
from aux.go_to import go_to_home, go_to_admin
from config import ADMIN_CREDENTIALS



def login_page():
    st.title("🔐 Login de Administrador")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Acesso Restrito")
        
        username = st.text_input("Usuário", key="login_username")
        password = st.text_input("Senha", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔓 Entrar", use_container_width=True, type="primary"):
                if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.admin_username = username
                    go_to_admin()
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Credenciais inválidas!")
        
        with col_btn2:
            if st.button("🏠 Voltar", use_container_width=True):
                go_to_home()
                st.rerun()
