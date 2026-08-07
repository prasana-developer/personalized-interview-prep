from flask import Blueprint, request, jsonify
from ..models import db, Question, Answer
from ..utils.gemini_agent import ai_pipeline

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/question/<int:question_id>', methods=['POST'])
def submit_answer(question_id):
    data = request.get_json() or {}
    user_answer = data.get('answer', '')

    if not user_answer or len(user_answer.strip()) < 3:
        return jsonify({'error': 'Please provide a non-empty answer'}), 400

    question = Question.query.get_or_404(question_id)

    # Call Feedback Agent
    eval_result = ai_pipeline.evaluate_answer(question.text, question.category, user_answer)

    # Check if answer record exists or create new
    existing_answer = Answer.query.filter_by(question_id=question.id).first()
    if existing_answer:
        existing_answer.user_answer = user_answer
        existing_answer.feedback = str(eval_result)
        db.session.commit()
        answer_id = existing_answer.id
    else:
        new_ans = Answer(question_id=question.id, user_answer=user_answer, feedback=str(eval_result))
        db.session.add(new_ans)
        db.session.commit()
        answer_id = new_ans.id

    return jsonify({
        "answer_id": answer_id,
        "question_id": question.id,
        "question_text": question.text,
        "category": question.category,
        "user_answer": user_answer,
        "feedback": eval_result
    }), 200

@feedback_bp.route('/history', methods=['GET'])
def get_answer_history():
    answers = Answer.query.order_by(Answer.created_at.desc()).all()
    res = []
    for a in answers:
        q = Question.query.get(a.question_id)
        res.append({
            "answer_id": a.id,
            "question_id": a.question_id,
            "question_text": q.text if q else "Question",
            "category": q.category if q else "general",
            "user_answer": a.user_answer,
            "created_at": a.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify(res), 200
