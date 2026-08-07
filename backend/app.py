import os
from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .models import db
from .routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure required folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(Config.BASE_DIR, 'instance'), exist_ok=True)

    # Initialize DB
    db.init_app(app)
    CORS(app, supports_credentials=True)

    # Root welcome health endpoint
    @app.route('/')
    def root():
        return jsonify({
            'status': 'online',
            'system': 'Personalized Interview Preparation System with Agentic AI',
            'api_base': '/api'
        })

    # Register Blueprint routes
    register_routes(app)

    return app

if __name__ == '__main__':
    flask_app = create_app()
    with flask_app.app_context():
        db.create_all()
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
