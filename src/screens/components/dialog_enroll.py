import streamlit as st
from src.database.db import enroll_student_to_subject, get_all_subjects, get_student_subjects
from src.database.config import supabase
import time

@st.dialog("Enroll in Subject")
def enroll_dialog():
    student_id = st.session_state.student_data['student_id']
    
    # --- Option 1: Quick Enroll via Code ---
    st.subheader("Quick Enroll")
    join_code = st.text_input('Enter Subject Code', placeholder='Eg. CS101')
    if st.button('Enroll via Code', type='primary', use_container_width=True):
        if join_code:
            res = supabase.table('subjects').select('subject_id, name, subject_code').eq('subject_code', join_code).execute()
            if res.data:
                subject = res.data[0]
                check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
                if check.data:
                    st.warning('You are already enrolled in this program')
                else:
                    enroll_student_to_subject(student_id, subject['subject_id'])
                    st.success(f'Succesfully enrolled in {subject["name"]}!')
                    time.sleep(1)
                    st.rerun()
            else:
                st.error("Invalid Subject Code")
        else:
            st.warning('Please enter a subject code')

    st.divider()

    # --- Option 2: Browse All Subjects ---
    st.subheader("Browse Subjects")
    
    # Get all subjects and student's current enrollments
    all_subjects = get_all_subjects()
    enrolled_data = get_student_subjects(student_id)
    enrolled_subject_ids = [item['subject_id'] for item in enrolled_data]

    if not all_subjects:
        st.info("No subjects available at the moment.")
        return

    # Use a scrollable container for many subjects if needed
    with st.container(height=300):
        for subject in all_subjects:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{subject['name']}** ({subject['subject_code']})")
                st.caption(f"Section {subject['section']}")
            with col2:
                if subject['subject_id'] in enrolled_subject_ids:
                    st.button("Joined", key=f"enrolled_{subject['subject_id']}", disabled=True, use_container_width=True)
                else:
                    if st.button("Enroll", key=f"enroll_{subject['subject_id']}", type="secondary", use_container_width=True):
                        enroll_student_to_subject(student_id, subject['subject_id'])
                        st.success(f"Enrolled in {subject['name']}!")
                        time.sleep(1)
                        st.rerun()
            st.divider()
