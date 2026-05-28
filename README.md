<div align="center">

<img src="https://i.ibb.co/YTYGn5qV/logo.png" alt="SnapClass Logo" width="120"/>

# SnapClass

### AI-Powered Attendance System with Face & Voice Recognition

[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Supabase](https://img.shields.io/badge/Database-Supabase-3FCF8E?logo=supabase&logoColor=white)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Take classroom attendance in seconds — just snap a photo or record audio.**

[Live Demo](https://snapclass-main.streamlit.app) · [Report Bug](https://github.com/akhil-c12/Face_recognition_attendance-System/issues) · [Request Feature](https://github.com/akhil-c12/Face_recognition_attendance-System/issues)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 📸 **Face Recognition** | Upload or capture a classroom photo and the AI identifies enrolled students using dlib + SVM |
| 🎙️ **Voice Recognition** | Record classroom audio — students say "I am present" and the AI matches voice embeddings |
| 👨‍🏫 **Teacher Dashboard** | Create subjects, take attendance, manage enrolled students, view & export records |
| 👩‍🎓 **Student Portal** | Login via Face ID, enroll in subjects with a code or QR scan, view attendance stats |
| 🔗 **QR Code Sharing** | Teachers share a join link / QR code so students can enroll instantly |
| 📊 **Attendance Records** | Filter, search, and download attendance as CSV |
| 🔒 **Secure Auth** | Teacher passwords hashed with bcrypt; student login is fully biometric |

---

## 🏗️ Architecture

```
face_attendance/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── .streamlit/
│   ├── secrets.toml.example        # Template for Supabase credentials
│   └── secrets.toml                # Your actual secrets (git-ignored)
│
└── src/
    ├── database/
    │   ├── config.py               # Supabase client initialization
    │   └── db.py                   # All database CRUD operations
    │
    ├── pipelines/
    │   ├── face_pipeline.py        # dlib face detection → SVM classifier
    │   └── voice_pipeline.py       # Resemblyzer voice embeddings → cosine similarity
    │
    └── screens/
        ├── home_screen.py          # Landing page (Teacher / Student portal)
        ├── teacher_screen.py       # Teacher login, dashboard, attendance flow
        ├── student_screen.py       # Student Face ID login, enrollment, dashboard
        ├── ui/
        │   └── base_layout.py      # Global CSS theme (Outfit font, Discord-style colors)
        └── components/
            ├── header.py           # Logo & title components
            ├── footer.py           # Footer placeholder
            ├── subject_card.py     # Reusable subject info card
            ├── dialog_add_photo.py         # Camera / upload dialog for attendance
            ├── dialog_enroll.py            # Student enrollment (code or browse)
            ├── dialog_auto_enroll.py       # Quick enroll via QR / deep link
            ├── dialog_voice_attendance.py  # Voice-based attendance dialog
            ├── dialog_attendance_results.py # Review & confirm attendance
            ├── dialogue_create_subject.py  # Create new subject dialog
            └── dialogue_share_subject.py   # Share subject via link / QR code
```

---

## 🧠 How It Works

### Face Recognition Pipeline

```
Classroom Photo → dlib Face Detector → 128D Face Embeddings → SVM Classifier → Student IDs
```

1. **Detection** — dlib's frontal face detector locates all faces in the image
2. **Encoding** — A pretrained ResNet model produces a 128-dimensional embedding per face
3. **Classification** — An SVM trained on enrolled student embeddings predicts identity
4. **Thresholding** — Euclidean distance ≤ 0.5 confirms a match

### Voice Recognition Pipeline

```
Audio Recording → Librosa VAD → Resemblyzer Embeddings → Cosine Similarity → Student IDs
```

1. **Segmentation** — Librosa splits audio into voiced segments (silence removed)
2. **Embedding** — Resemblyzer's pretrained encoder creates a speaker embedding per segment
3. **Matching** — Cosine similarity against enrolled voice embeddings identifies speakers
4. **Thresholding** — Similarity ≥ 0.65 confirms a match

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | [Streamlit](https://streamlit.io) with custom CSS (Outfit font, Discord color palette) |
| **Face AI** | [dlib](http://dlib.net) + [face_recognition_models](https://github.com/ageitgey/face_recognition_models) + [scikit-learn](https://scikit-learn.org) SVM |
| **Voice AI** | [Resemblyzer](https://github.com/resemble-ai/Resemblyzer) + [Librosa](https://librosa.org) |
| **Database** | [Supabase](https://supabase.com) (PostgreSQL) |
| **Auth** | [bcrypt](https://github.com/pyca/bcrypt) for teacher passwords, biometric for students |
| **QR Codes** | [Segno](https://github.com/heuer/segno) |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **CMake** — required to build dlib (`pip install cmake`)
- A free [Supabase](https://supabase.com) project

### 1. Clone the repository

```bash
git clone https://github.com/akhil-c12/Face_recognition_attendance-System.git
cd Face_recognition_attendance-System
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Supabase credentials

```bash
# Copy the example and fill in your real keys
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

### 5. Set up the database

Create the following tables in your Supabase dashboard:

<details>
<summary><b>📋 SQL Schema (click to expand)</b></summary>

```sql
-- Teachers table
CREATE TABLE teachers (
    teacher_id SERIAL PRIMARY KEY,
    username   TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    name       TEXT NOT NULL
);

-- Students table
CREATE TABLE students (
    student_id      SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    face_embedding  JSONB,
    voice_embedding JSONB
);

-- Subjects table
CREATE TABLE subjects (
    subject_id   SERIAL PRIMARY KEY,
    subject_code TEXT NOT NULL,
    name         TEXT NOT NULL,
    section      TEXT NOT NULL,
    teacher_id   INTEGER REFERENCES teachers(teacher_id)
);

-- Subject ↔ Student enrollment
CREATE TABLE subject_students (
    id         SERIAL PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects(subject_id),
    student_id INTEGER REFERENCES students(student_id),
    UNIQUE(subject_id, student_id)
);

-- Attendance logs
CREATE TABLE attendance_logs (
    id         SERIAL PRIMARY KEY,
    subject_id INTEGER REFERENCES subjects(subject_id),
    student_id INTEGER REFERENCES students(student_id),
    timestamp  TIMESTAMPTZ NOT NULL,
    is_present BOOLEAN DEFAULT TRUE
);
```

</details>

### 6. Run the app

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**.

---

## 📸 Screenshots

| Home Screen | Teacher Dashboard | Student Portal |
|---|---|---|
| Choose Teacher or Student portal | Take attendance, manage subjects | Face ID login, enroll in subjects |

---

## 🌐 Deployment

This app is ready for [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set **Main file path** to `app.py`
4. Add your `SUPABASE_URL` and `SUPABASE_KEY` in the **Secrets** section
5. Deploy 🚀

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Built with ❤️ by [Akhil](https://github.com/akhil-c12)**

</div>
