import os
from flask import Blueprint
from .auth import auth_bp
from .resume import resume_bp
from .dashboard import dashboard_bp
from .feedback import feedback_bp

def register_routes(app):
    api = Blueprint('api', __name__)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(resume_bp, url_prefix='/api/resume')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    app.register_blueprint(api)
