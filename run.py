from main import __call__
from main.extensions import db
from main.models import Role,Guides,User,Specifics,Symptoms,Permission
from flask_migrate import Migrate
import os

app = __call__(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app,db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db,app=app,User=User,Guides=Guides,Role=Role,Permission=Permission,Specifics=Specifics,Symptoms=Symptoms)