from main import __call__
from main.extensions import db
from main.models import Role,Guides,User,Specifics,Symptoms,Permission,Doctor
from main.schema import user_schema,users_schema,GuideSchema,comment_schema,comments_schema
from flask_migrate import Migrate
import os
import firebase_admin

app = __call__(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app,db)
#firebase_admin.initialize_app(app.config['CRED'])
firebase_admin.initialize_app()

@app.shell_context_processor
def make_shell_context():
    return dict(user_schema=user_schema,comment_schema=comment_schema,comments_schema=comments_schema,Permission=Permission,users_schema=users_schema,gscheme=GuideSchema,db=db,app=app,User=User,Guides=Guides,Role=Role,Specifics=Specifics,Symptoms=Symptoms,Doctor=Doctor)