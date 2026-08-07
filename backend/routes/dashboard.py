import json
from flask import Blueprint, jsonify
from ..models import db, User, Resume, Analysis, Question, Answer

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def get_stats():
    total_resumes = Resume.query.count()
    analyses = Analysis.query.order_by(Analysis.created_at.desc()).all()
    
    avg_ats = 0
    if analyses:
        avg_ats = round(sum(a.ats_score for a in analyses) / len(analyses), 1)

    total_answers = Answer.query.count()

    recent_history = []
    for a in analyses[:5]:
        r = Resume.query.get(a.resume_id)
        recent_history.append({
            "id": a.id,
            "filename": r.filename if r else "Resume.pdf",
            "ats_score": a.ats_score,
            "result": a.result,
            "date": a.created_at.strftime('%b %d, %Y')
        })

    return jsonify({
        "total_resumes_analyzed": total_resumes,
        "avg_ats_score": avg_ats,
        "total_mock_answers": total_answers,
        "recent_history": recent_history
    }), 200
