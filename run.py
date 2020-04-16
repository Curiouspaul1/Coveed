from main import __call__
from main.extensions import db
from flask_migrate import Migrate
import os

app = __call__(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app,db)