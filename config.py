import os
from firebase_admin import credentials

basedir = os.getcwd()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    ADMIN_EMAIL = ''
    APP_EMAIL = os.environ.get('APP_EMAIL')
    AGENT_EMAILS = os.environ.get('AGENT_EMAILS')
    FIREBASE_KEY = os.getenv('FIREBASE_KEY').replace('\\n', '\n')
    FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL')

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'coved-dev.sqlite') or os.getenv('DEV_URI')
    DEBUG = True

class TestingConfig(Config):
    TESTING =True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'coveed-test.sqlite') or os.getenv('TEST_URI')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    FLASK_ENV='production'


config = {
    'development':DevelopmentConfig,
    'Testing':TestingConfig,
    'Production':ProductionConfig,

    'default':DevelopmentConfig
}

