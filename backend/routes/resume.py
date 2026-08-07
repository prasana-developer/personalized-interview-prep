import os
import json
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from ..config import Config
from ..models import db, User, Resume, Analysis, Question
from ..utils.resume_parser import extract_text_from_file
from ..utils.gemini_agent import ai_pipeline

resume_bp = Blueprint('resume', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resume_bp.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files and 'sample_text' not in request.form:
        return jsonify({'error': 'No file or text provided'}), 400

    user_id = request.form.get('user_id', 1)
    target_role = request.form.get('target_role', 'Software Engineer').strip() or 'Software Engineer'

    raw_text = ""
    filename = "pasted_resume.txt"

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(upload_path)
            raw_text = extract_text_from_file(upload_path)
        else:
            return jsonify({'error': 'Invalid file format. Please upload PDF, DOCX, or TXT.'}), 400
    else:
        raw_text = request.form.get('sample_text', '')

    if not raw_text or len(raw_text.strip()) < 10:
        raw_text = "Experienced Software Engineer with proficiency in Python, React, Flask, JavaScript, SQL databases, Git, and cloud microservices."

    # Save Resume Record
    new_resume = Resume(user_id=user_id, filename=filename, raw_text=raw_text)
    db.session.add(new_resume)
    db.session.commit()

    # Trigger Agentic AI Analysis for Target Role
    ai_result = ai_pipeline.analyze_resume(raw_text, target_role=target_role)

    # Save Analysis Record
    new_analysis = Analysis(
        resume_id=new_resume.id,
        target_role=target_role,
        ats_score=ai_result.get('ats_score', 80),
        result=ai_result.get('result', 'Selected'),
        explanation=ai_result.get('explanation', ''),
        skill_gaps=json.dumps(ai_result.get('missing_skills', [])),
        roadmap=json.dumps(ai_result.get('roadmap', []))
    )
    db.session.add(new_analysis)
    db.session.commit()

    # Save Generated Questions
    questions_dict = ai_result.get('questions', {})
    saved_questions = []

    for cat, q_list in questions_dict.items():
        for q_text in q_list:
            q_obj = Question(analysis_id=new_analysis.id, category=cat, text=q_text)
            db.session.add(q_obj)
            db.session.flush()
            saved_questions.append({
                "id": q_obj.id,
                "category": cat,
                "text": q_text
            })

    db.session.commit()

    return jsonify({
        "message": "Resume scanned and analyzed successfully",
        "resume_id": new_resume.id,
        "analysis_id": new_analysis.id,
        "filename": filename,
        "target_role": target_role,
        "ats_score": new_analysis.ats_score,
        "result": new_analysis.result,
        "matched_skills": ai_result.get('matched_skills', []),
        "required_job_skills": ai_result.get('required_job_skills', []),
        "missing_skills": ai_result.get('missing_skills', []),
        "explanation": new_analysis.explanation,
        "certifications": ai_result.get('certifications', []),
        "roadmap": ai_result.get('roadmap', []),
        "questions": saved_questions
    }), 200

@resume_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    questions = Question.query.filter_by(analysis_id=analysis.id).all()

    q_list = [{"id": q.id, "category": q.category, "text": q.text} for q in questions]

    return jsonify({
        "analysis_id": analysis.id,
        "resume_id": analysis.resume_id,
        "target_role": getattr(analysis, 'target_role', 'Software Engineer'),
        "ats_score": analysis.ats_score,
        "result": analysis.result,
        "explanation": analysis.explanation,
        "missing_skills": json.loads(analysis.skill_gaps) if analysis.skill_gaps else [],
        "roadmap": json.loads(analysis.roadmap) if analysis.roadmap else [],
        "questions": q_list
    }), 200
