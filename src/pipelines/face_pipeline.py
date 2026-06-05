from PIL import ImageFile
import dlib
import numpy as np
import face_recognition_models
import streamlit as st

from src.database.db import get_all_students

@st.cache_resource(show_spinner=False)
def load_dlib_models():
    detector=dlib.get_frontal_face_detector()
    sp=dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec=dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector,sp,facerec

def get_face_embeddings(image_np):
    detector,sp,facerec=load_dlib_models()
    faces=detector(image_np,1)

    encodings=[]
    for face in faces:
        shape=sp(image_np,face)
        face_descriptor=facerec.compute_face_descriptor(image_np,shape,1)
        encodings.append(np.array(face_descriptor))
    return encodings

@st.cache_resource(show_spinner=False)
def get_student_database():
    student_db = get_all_students()
    if not student_db:
        return []

    processed_db = []
    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            processed_db.append({
                'student_id': student.get('student_id'),
                'embedding': np.array(embedding)
            })
    return processed_db

def train_classifier():
    st.cache_resource.clear()
    return True

def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)
    detected_student = {}

    student_db = get_student_database()

    if not student_db:
        return detected_student, [], len(encodings)

    all_student_ids = [s['student_id'] for s in student_db]
    resemblance_threshold = 0.5

    for encoding in encodings:
        best_match_id = None
        min_distance = float('inf')

        for student in student_db:
            distance = np.linalg.norm(student['embedding'] - encoding)
            if distance < min_distance:
                min_distance = distance
                best_match_id = student['student_id']

        if min_distance <= resemblance_threshold:
            detected_student[best_match_id] = True

    return detected_student, all_student_ids, len(encodings)





