from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import create_student
import streamlit as st
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.header import header_dashboard
from src.screens.components.footer import footer_dashboard
from PIL import Image
import numpy as np  
from src.database.db import get_all_students
from src.pipelines.face_pipeline import predict_attendance,get_face_embeddings,train_classifier
from src.screens.components.dialogue_create_subject import create_subject_dialog
import time



def student_dashboard():
    student_data=st.session_state.student_data
    student_name=student_data['name'] if isinstance(student_data,dict) else student_data[0]['name']

    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        st.header(f"Welcome, {student_name}")
        if st.button("Logout", type='secondary', key='student_logoutbtn'):
            del st.session_state.student_data
            if 'is_logged_in' in st.session_state:
                del st.session_state.is_logged_in
            st.rerun()

    if 'welcome_msg' in st.session_state:
        st.toast(st.session_state.welcome_msg)
        del st.session_state.welcome_msg

    if 'current_student_tab' not in st.session_state:
        st.session_state.current_student_tab='take_attendance'

    tab1,tab2,tab3=st.columns(3)
    with tab1:
        if st.button('Take Attendance',type='tertiary',use_container_width=True,icon=':material/face_retouching_natural:'):
            st.session_state.current_student_tab='take_attendance'
            st.rerun()
    with tab2:
        if st.button('Manage Subjects',type='primary',use_container_width=True,icon=':material/menu_book:'):
            st.session_state.current_student_tab='manage_subjects'
            st.rerun()

    with tab3:
        if st.button('Attendance Records',type='tertiary',use_container_width=True,icon=':material/assignment:'):
            st.session_state.current_student_tab='attendance_records'
            st.rerun()

    st.divider()


    footer_dashboard()



def student_screen():

    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return
    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.markdown("<h2 style='text-align: center;'>Login using FaceID</h2>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    show_registration=False
    photo_source = st.camera_input("position your face in center")

    if photo_source:
        img=np.array(Image.open(photo_source))
        with st.spinner('Ai is Scanning..'):
            detected,all_ids,num_faces=predict_attendance(img)

            if num_faces==0:
                st.warning('No Face Detected')
            elif num_faces>1:
                st.error("Error : Multiple faces detected")
            else:
                if detected:
                    student_id=list(detected.keys())[0]
                    all_students=get_all_students()
                    student=next((s for s in all_students if s['student_id']==student_id),None)

                    if student:
                        st.session_state.is_logged_in=True
                        st.session_state.user_role='student'
                        st.session_state.student_data=student
                        st.session_state.welcome_msg=f"Welcome Back {student['name']}"
                        st.rerun()
                    else:
                        st.warning("You might be new! Please register below.")
                        show_registration=True
                else:
                    st.warning("You might be new! Please register below.")
                    show_registration=True
    if show_registration:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name=st.text_input("Enter your Name",placeholder='Student Name')

            st.subheader('Optional:Voice Enrollment')
            st.info("Enroll your for only attrndance")

            audio_data=None

            try:
                audio_data=st.audio_input('Record a short phrase like I am present,My name is StudentX')
            except Exception:
                st.error('Audion Data failed')

            if st.button('Create Account',type='primary'):
                if new_name:
                    with st.spinner('Creating profile'):
                        img=np.array(Image.open(photo_source))
                        encodings=get_face_embeddings(img)
                        if encodings:
                            face_emb=encodings[0].tolist()
                            voice_emb=None

                            if audio_data:
                                voice_emb=get_voice_embedding(audio_data.read())
                            response_data=create_student(new_name,face_emb,voice_emb)
                            st.success("Account Created Successfully")
                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in=True
                                st.session_state.user_role='student'
                                st.session_state.student_data=response_data
                                st.session_state.welcome_msg=f'Profile Created ! Hi {new_name}'
                                st.rerun()
                            else:
                                st.error('profile creation failed')
                        else:
                            st.error('Face Encoding Failed')    
                            
                else:
                    st.warning('Please Enter Your Name')



    footer_dashboard() 