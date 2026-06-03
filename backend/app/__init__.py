import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from app.config import Config
from app.extensions import init_extensions, db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    # 初始化JWT
    jwt = JWTManager(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        print(f"Invalid token: {error_string}")
        return jsonify({'msg': 'Invalid token', 'error': str(error_string)}), 422

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        print(f"Unauthorized: {error_string}")
        return jsonify({'msg': 'Missing authorization token', 'error': str(error_string)}), 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        print(f"Expired token: {jwt_data}")
        return jsonify({'msg': 'Token has expired', 'error': str(jwt_data)}), 422

    @jwt.invalid_token_loader
    def bad_request_callback(error_string):
        print(f"Bad request: {error_string}")
        return jsonify({'msg': 'Bad token', 'error': str(error_string)}), 422

    init_extensions(app)

    from app.api import register_blueprints
    register_blueprints(app)

    @app.route('/')
    def index():
        return jsonify({
            'name': 'PartTech API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'login': '/api/auth/login'
            }
        })

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'PartTech API Running'})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': '资源不存在'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': '服务器内部错误'}), 500

    return app