Name:Prasanna Venkatachalapathy S
Roll No:24AD1172
Dept:ADS - B , 3rd - year


# Personalized Interview Preparation System

A full‑stack web application that helps job seekers prepare for interviews using **Agentic AI** (Google Gemini). Users can register, upload their resume, get an ATS score, see skill‑gap analysis, receive a personalized learning roadmap, and practice interview questions with AI feedback.

## Project Structure
```
personalized_interview_prep/
├─ backend/
│   ├─ app.py
│   ├─ requirements.txt
│   ├─ config.py
│   ├─ models.py
│   ├─ routes/
│   │   ├─ __init__.py
│   │   ├─ auth.py
│   │   ├─ resume.py
│   │   ├─ dashboard.py
│   │   └─ feedback.py
│   ├─ services/
│   │   ├─ __init__.py
│   │   ├─ gemini_agent.py
│   │   ├─ resume_parser.py
│   │   ├─ ats_scoring.py
│   │   ├─ skill_gap.py
│   │   ├─ question_generator.py
│   │   └─ feedback_engine.py
│   └─ utils/
│       └─ auth_helpers.py
├─ frontend/
│   ├─ vite.config.js
│   ├─ package.json
│   ├─ tailwind.config.js
│   ├─ postcss.config.js
│   └─ src/
│       ├─ main.jsx
│       ├─ App.jsx
│       ├─ index.css
│       ├─ components/
│       │   ├─ Navbar.jsx
│       │   ├─ LoginForm.jsx
│       │   ├─ RegisterForm.jsx
│       │   ├─ Dashboard.jsx
│       │   ├─ ResumeUploader.jsx
│       │   ├─ ScoreChart.jsx
│       │   ├─ ResultBadge.jsx
│       │   ├─ SkillGapList.jsx
│       │   ├─ Roadmap.jsx
│       │   ├─ QuestionList.jsx
│       │   └─ AnswerFeedback.jsx
│       └─ services/
│           └─ api.js
├─ .env.example
└─ .gitignore
```

## Prerequisites
- **Python 3.11+**
- **Node.js >= 20**
- Google Gemini API key (create at https://ai.google.dev)

## Setup
### Backend
```bash
cd backend
python -m venv venv
# Windows activation
venv\\Scripts\\activate
pip install -r requirements.txt
# Copy .env.example to .env and fill in your keys
cp .env.example .env
python app.py
```
The API will be available at `http://localhost:5000`.

### Frontend
```bash
cd ../frontend
npm install
npm run dev
```
The dev server runs at `http://localhost:5173` and proxies API calls to the Flask backend.

## Features
- User registration & login (JWT auth)
- Resume upload (PDF/DOCX) → text extraction via **PyMuPDF** / **python-docx**
- Multiple AI agents using **Google Gemini**:
  - ATS scoring (0‑100)
  - Skill‑gap analysis & certification suggestions
  - Personalized learning roadmap generation
  - Interview question generation (technical, HR, behavioral)
  - Real‑time answer feedback
- Data persisted in **SQLite**
- Modern responsive UI built with **React**, **Vite**, **Tailwind CSS**, and **Chart.js**

## License
MIT
