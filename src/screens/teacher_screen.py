from src.database.db import create_teacher
import streamlit as st
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.header import header_dashboard
from src.screens.components.footer import footer_dashboard

from src.database.db import check_teacher_exists,create_teacher,teacher_login

def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if st.session_state.get('teacher_logged_in'):
        st.markdown("<h2 style='text-align: center;'>Teacher Dashboard</h2>", unsafe_allow_html=True)
        st.write(f"Welcome, {st.session_state['teacher_data']['name']}!")
        if st.button("Logout", key="logoutbtn"):
            st.session_state['teacher_logged_in'] = False
            st.session_state['teacher_data'] = None
            st.rerun()
        return

    if 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()

def login_teacher(username,password):
    if not username or not password:
        return false
    teacher=teacher_login(username,password)
    if teacher:
        st.session_state.user_role='teacher'
        st.session_state.teacher_data=teacher
        st.session_state.teacher_logged_in=True
        return True
    return False
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
        if st.button('Register Instead', type="primary", icon=':material/passkey:', key='registerbtn', use_container_width=True):
            st.session_state.teacher_login_type = 'register'
            st.rerun()

    with btnc2:
        if st.button('Login', type="primary", icon=':material/login:', key='loginbtn', use_container_width=True):
            user = teacher_login(teacher_username, teacher_pass)
            if user:
                st.success("Logged in successfully!")
                st.session_state['teacher_logged_in'] = True
                st.session_state['teacher_data'] = user
                st.rerun()
            else:
                st.error("Invalid username or password")

def register_teacher(teacher_username,teacher_name,teacher_pass,teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass or not teacher_pass_confirm:
        st.error("All feilds are required!")
        return False,"All feilds are required!"

    if teacher_pass != teacher_pass_confirm:
        return False,"Passwords do not match"

    if check_teacher_exists(teacher_username):
        return False,"Username already taken"

    try:
        create_teacher(teacher_username,teacher_pass,teacher_name)
        return True,"Teacher registered successfully"
    except Exception as e:
        return False,str(e)



def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='registerbackbtn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<h2 style='text-align: center;'>Register your teacher profile</h2>", unsafe_allow_html=True)

    st.write("")
    st.write("")


    teacher_username = st.text_input("Enter username", placeholder='username')

    teacher_name = st.text_input("Enter name", placeholder='Name')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', key='registernowbtn', use_container_width=True):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                st.session_state.teacher_login_type = 'login'
            else:
                st.error(message)

    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', key='logininsteadbtn', use_container_width=True):
            st.session_state.teacher_login_type = 'login'
