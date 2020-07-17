from main import __call__
from main.extensions import db
from main.models import Role,Guides,User,Specifics,Symptoms,Permission,Doctor
from main.schema import user_schema,users_schema,GuideSchema,comment_schema,comments_schema
from flask_migrate import Migrate
import os
import firebase_admin
from firebase_admin import credentials

app = __call__(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app,db)
key,email = app.config['FIREBASE_KEY'],app.config['FIREBASE_CLIENT_EMAIL']
cred = credentials.Certificate(
{
        'type':"service_account",
        'project_id':"coveed-19",
        "private_key_id": "abf956b68dd7ac9a29dbd584d7c6c1e7990050e5",
        'private_key':key,
        'client_email':email,
        "client_id": "106525062045074392577",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-5pl26%40coveed-19.iam.gserviceaccount.com"
    }
)
print(cred)
firebase_admin.initialize_app(cred)

@app.shell_context_processor
def make_shell_context():
    return dict(user_schema=user_schema,comment_schema=comment_schema,comments_schema=comments_schema,Permission=Permission,users_schema=users_schema,gscheme=GuideSchema,db=db,app=app,User=User,Guides=Guides,Role=Role,Specifics=Specifics,Symptoms=Symptoms,Doctor=Doctor)