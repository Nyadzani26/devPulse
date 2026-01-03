import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads (static paths)
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024 # 4MB

class DevelopmentConfig(Config):
    DEBUG = True
    # local SQLite DB
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'devpulse.db')

class ProductionConfig(Config):
    DEBUG = False
    # Production DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        ('sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'prod_devpulse.db'))

config_options = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
