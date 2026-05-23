from src.database.db import create_teacher
import streamlit as st
from src.screens.ui.base_layout import style_background_dashboard, style_base_layout
from src.screens.components.header import header_dashboard
from src.screens.components.footer import footer_dashboard
from PIL import Image
import numpy as np  
from src.database.db import get_all_students
from src.pipelines.face_pipeline import predict_attendance

def student_screen():

    style_background_dashboard()
    style_base_layout()

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

    photo_source = st.camera_input("position your face in center")

    if photo_source:
        image = Image.open(photo_source)
        image_np = np.array(image)

        detected_students, all_students, total_faces = predict_attendance(image_np)

        st.success(f"Detected {len(detected_students)} student(s)")
        st.write("Detected IDs:", list(detected_students.keys()))
    footer_dashboard() 