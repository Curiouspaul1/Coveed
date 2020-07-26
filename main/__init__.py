#! python3

from flask import Flask
from .extensions import db,ma,cors
from config import config
import os

def __call__(config_object):
    app = Flask(__name__)
    app.config.from_object(config[config_object])
    app.config['SECRET_KEY'] = os.urandom(24)

    db.init_app(app)
    ma.init_app(app)
<<<<<<< HEAD
    #firebase_admin.initialize_app()
=======
>>>>>>> 412787909fb42aa332016699217946809d9228d8
    cors.init_app(app, resources={r"/api/*":{"origins":"*"},r"/doctors/*":{"origins":"*"}})

    # register blurprint
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint,url_prefix='/api')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint,url_prefix='/admin')

    from .doctors import doctor as doc_blueprint
    app.register_blueprint(doc_blueprint,url_prefix='/doctors')
    
    return app
