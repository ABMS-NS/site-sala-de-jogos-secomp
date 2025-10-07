import streamlit as st



def go_to_home():
    st.session_state.current_page = 'home'
    st.session_state.logged_in = False

def go_to_login():
    st.session_state.current_page = 'login'

def go_to_admin():
    st.session_state.current_page = 'admin'
