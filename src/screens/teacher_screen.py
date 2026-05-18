import streamlit as st
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.header import header_dashboard
from src.screens.components.footer import footer_dashboard



def teacher_screen():

    style_background_dashboard()
    style_base_layout()
    teacher_screen_login()


def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
    st.write("")
    st.write("")


    teacher_username = st.text_input("Enter Username", placeholder='username')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)
    with btnc1:
        st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch')
    with btnc2:
        st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch')
