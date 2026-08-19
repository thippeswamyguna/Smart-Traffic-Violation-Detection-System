import os
from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from models import db
from routes.auth import auth_bp
from routes.violations import violations_bp
from routes.detect import detect_bp

def create_app():
    # Set templates and static paths to local directories
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates'),
                static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static'))
    
    app.config.from_object(Config)
    
    # Enable Cross-Origin Resource Sharing
    CORS(app)
    
    # Initialize SQLAlchemy models
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(violations_bp, url_prefix='/api/violations')
    app.register_blueprint(detect_bp, url_prefix='/api/detect')
    
    # Frontend Page Rendering Routes
    @app.route('/')
    def login_page():
        return render_template('index.html')
        
    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')
        
    @app.route('/upload')
    def upload_page():
        return render_template('upload.html')
        
    @app.route('/live')
    def live_page():
        return render_template('live.html')
        
    @app.route('/violations')
    def violations_page():
        return render_template('violations.html')
        
    @app.route('/report')
    def report_page():
        return render_template('report.html')
        
    # Ensure static upload directory is created
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Run server on port 5000 in debug mode
    app.run(host='127.0.0.1', port=5000, debug=True)
