
import streamlit as st
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.header import header_dashboard
from src.screens.components.footer import footer_dashboard
from src.screens.components.dialogue_create_subject import create_subject_dialog
from src.screens.components.subject_card import subject_card
from src.database.db import check_teacher_exists,create_teacher,teacher_login,get_teacher_subjects


def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if st.session_state.get('teacher_logged_in'):
        teacher_dashboard()
        return

    if 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()

def teacher_dashboard():
    teacher_data=st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        st.header(f"Welcome, {teacher_data['name']}")
        if st.button("Logout", type='secondary', key='logoutbtn'):
            st.session_state['teacher_logged_in'] = False
            if 'teacher_data' in st.session_state:
                del st.session_state.teacher_data
            st.rerun()

    if 'teacher_welcome_msg' in st.session_state:
        st.toast(st.session_state.teacher_welcome_msg)
        del st.session_state.teacher_welcome_msg

    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab='take_attendance'

    tab1,tab2,tab3=st.columns(3)
    with tab1:
        if st.button('Take Attendance',type='tertiary',use_container_width=True,icon=':material/face_retouching_natural:'):
            st.session_state.current_teacher_tab='take_attendance'
            st.rerun()
    with tab2:
        if st.button('Manage Subjects',type='primary',use_container_width=True,icon=':material/menu_book:'):
            st.session_state.current_teacher_tab='manage_subjects'
            st.rerun()

    with tab3:
        if st.button('Attendance Records',type='tertiary',use_container_width=True,icon=':material/assignment:'):
            st.session_state.current_teacher_tab='attendance_records'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab=="take_attendance":
        teacher_tab_take_attendance()
    elif st.session_state.current_teacher_tab=="manage_subjects":
        teacher_tab_manage_subjects()
    elif st.session_state.current_teacher_tab=="attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    st.header("Take Attendance")

def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects')
    with col2:
        if st.button('Create New Subject', use_container_width=True):
            create_subject_dialog(teacher_id)

    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
            )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")

def teacher_tab_attendance_records():
    st.header("Attendance Records")

def login_teacher(username,password):
    if not username or not password:
        return False
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
                st.session_state['teacher_logged_in'] = True
                st.session_state['teacher_data'] = user
                st.session_state['teacher_welcome_msg'] = f"Welcome back {user['name']}!"
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
                if message == "Username already taken":
                    st.warning(message)
                else:
                    st.error(message)

    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', key='logininsteadbtn', use_container_width=True):
            st.session_state.teacher_login_type = 'login'
