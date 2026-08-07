from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resumes = db.relationship('Resume', backref='user', lazy=True)

class Resume(db.Model):
    __tablename__ = 'resumes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    raw_text = db.Column(db.Text, nullable=True)

    analysis = db.relationship('Analysis', uselist=False, backref='resume')

class Analysis(db.Model):
    __tablename__ = 'analyses'
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    target_role = db.Column(db.String(100), nullable=True, default='Software Engineer')
    ats_score = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(50), nullable=False)  # Selected / Needs Improvement / Rejected
    explanation = db.Column(db.Text, nullable=True)
    skill_gaps = db.Column(db.Text, nullable=True)  # JSON stringified list
    roadmap = db.Column(db.Text, nullable=True)     # JSON stringified roadmap
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', backref='analysis', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # technical, hr, behavioral
    text = db.Column(db.Text, nullable=False)

    answer = db.relationship('Answer', uselist=False, backref='question')

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
