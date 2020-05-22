from flask import Flask
from .extensions import db,ma
from config import config
import os

def __call__(config_object):
    app = Flask(__name__)
    app.config.from_object(config[config_object])
    app.config['SECRET_KEY'] = os.urandom(24)

    db.init_app(app)
    ma.init_app(app)

    # register blurprint
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)
    
    return app
