import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-pulse-extremely-secret-key-123'
    
    # Database
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'devpulse.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads (just in case we want dev avatars later)
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB

config_options = {
    'development': Config,
    'default': Config
}
