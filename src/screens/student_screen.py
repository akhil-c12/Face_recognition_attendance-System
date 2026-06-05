import streamlit as st
import time
import numpy as np
from PIL import Image
from src.database.db import (
    get_all_students, 
    create_student, 
    get_student_subjects, 
    get_student_attendance, 
    get_attendance_logs_for_subjects,
    unenroll_student_to_subject
)
from src.pipelines.voice_pipeline import get_voice_embedding
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.header import header_dashboard
from src.screens.components.footer import footer_dashboard
from src.screens.components.subject_card import subject_card
from src.screens.components.dialog_enroll import enroll_dialog

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"Welcome, {student_data['name']}")
        if st.button("Logout", type='secondary', key='logoutbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            if 'student_data' in st.session_state:
                del st.session_state.student_data
            st.session_state.is_registering = False
            st.rerun()

    st.write('')

    # Overall summary calculation
    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    subject_ids = [
        sub_node['subjects']['subject_id']
        for sub_node in subjects
        if sub_node.get('subjects')
    ]
    subject_logs = get_attendance_logs_for_subjects(subject_ids)

    subject_sessions_map = {}
    for log in subject_logs:
        subject_sessions_map.setdefault(log['subject_id'], set()).add(log['timestamp'])

    stats_map = {}
    for log in logs:
        sid = log['subject_id']
        stats_map.setdefault(sid, set())
        if log.get('is_present'):
            stats_map[sid].add(log['timestamp'])

    total_classes_all = 0
    attended_classes_all = 0
    for sub_node in subjects:
        sub = sub_node['subjects']
        sid = sub['subject_id']
        total_sessions = len(subject_sessions_map.get(sid, set()))
        attended_sessions = len(stats_map.get(sid, set()))
        total_sessions = max(total_sessions, attended_sessions)
        total_classes_all += total_sessions
        attended_classes_all += attended_sessions

    overall_percentage = (
        round((attended_classes_all / total_classes_all) * 100, 1)
        if total_classes_all
        else 0
    )

    st.subheader("📊 Overall Attendance Summary")
    met1, met2, met3 = st.columns(3)
    with met1:
        st.metric("Total Attendance", f"{overall_percentage}%")
    with met2:
        st.metric("Total Classes", total_classes_all)
    with met3:
        st.metric("Attended", attended_classes_all)

    st.divider()
    c1, c2 = st.columns([2, 1], vertical_alignment='center')
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', use_container_width=True, key='enroll_btn_dashboard'):
            enroll_dialog()

    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']
        total_sessions = len(subject_sessions_map.get(sid, set()))
        attended_sessions = len(stats_map.get(sid, set()))
        total_sessions = max(total_sessions, attended_sessions)
        attendance_percentage = (
            round((attended_sessions / total_sessions) * 100, 1)
            if total_sessions
            else 0
        )
        
        def unenroll_button():
            if st.button("Unenroll from this course", type='secondary', key=f"unenroll_{sid}", use_container_width=True, icon=':material/delete_forever:'):
                unenroll_student_to_subject(student_id, sid)
                st.toast(f"Unenrolled from {sub['name']} successfully!")
                st.rerun()

        with cols[i % 2]:
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    ('📅', 'Total', total_sessions),
                    ('✅', 'Attended', attended_sessions),
                    ('📊', 'Attendance', f"{attendance_percentage:g}%"),
                ],
                footer_callback=unenroll_button
            )
    footer_dashboard()

def student_screen():
    style_background_dashboard()
    style_base_layout()
    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):    
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using FaceID')
    st.write('')
    st.write('')

    show_registration = False
    photo_source = st.camera_input("Position your face in the center")

    if photo_source:
        img = np.array(Image.open(photo_source))
        with st.spinner('AI is scanning..'):
            detected, all_ids, num_faces = predict_attendance(img)
            if num_faces == 0:
                st.warning('Face not found!')
            elif num_faces > 1:
                st.warning('Multiple faces found')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id), None)
                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back {student['name']}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info('Face not recognized! You might be a new student!')
                    show_registration = True

    if show_registration:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name = st.text_input("Enter your name", placeholder='E.g. Hamza Rizvi')
            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll your for voice only attendance")
            audio_data = None
            try:
                audio_data = st.audio_input('Record a short phrase like I am present, My name is Akash.')       
            except Exception:
                st.error('Audio Data failed!')

            if st.button('Create Account', type='primary'):
                if st.session_state.get('is_registering'):
                    return
                st.session_state.is_registering = True
                if new_name:
                    with st.spinner('Creating profile..'):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()
                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())
                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)
                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f"Profile Created! Hi {new_name}!")
                                time.sleep(1)
                                st.session_state.is_registering = False
                                st.rerun()
                        else:
                            st.session_state.is_registering = False
                            st.error('Couldnt capture your facial features for registration')
                else:
                    st.session_state.is_registering = False
                    st.warning('Please enter your name!')
    footer_dashboard()
