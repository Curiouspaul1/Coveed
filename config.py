import os

basedir = os.getcwd()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('secret')

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'coveed-dev.sqlite') or os.getenv('DEV_URI')
    DEBUG = True

class TestingConfig(Config):
    TESTING =True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'coveed-test.sqlite') or os.getenv('TEST_URI')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'coveed-prod.sqlite') or os.getenv('PROD_URI')


config = {
    'development':DevelopmentConfig,
    'Testing':TestingConfig,
    'Production':ProductionConfig,

    'default':DevelopmentConfig
}

