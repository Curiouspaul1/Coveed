from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS

ma = Marshmallow()
db = SQLAlchemy()
cors = CORS()
