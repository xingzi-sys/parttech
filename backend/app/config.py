import os
from datetime import timedelta

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'parttech-secret-key-2024')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(BASE_DIR), 'instance', 'parttech.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'parttech-jwt-secret-2024')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    PAGINATION_PER_PAGE = 20