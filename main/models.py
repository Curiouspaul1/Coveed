from main import db,ma
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    tel = db.Column(db.String(50))
    country = db.Column(db.String(50))
    state = db.Column(db.String(50))
    address = db.Column(db.String(200))
    age = db.Column(db.Integer)
    username = db.Column(db.String(100),unique=True)
    user_id = db.Column(db.String(100),unique=True)
    sign_up_date = db.Column(db.DateTime(), default=datetime.utcnow)
    sign_up_method = db.Column(db.String(100))
    symptoms = db.relationship('Symptoms',backref='patient')

class Symptoms(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True)
    cough = db.Column(db.Boolean,default=False)
    resp = db.Column(db.Boolean,default=False)
    fever = db.Column(db.Boolean,default=False)
    fatigue = db.Column(db.Boolean,default=False)
    other = db.Column(db.String(200))
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    specifics = db.relationship('Specifics',backref='symptom',uselist=False)

class Specifics(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    cough_degree = db.Column(db.String(50))
    fever_degree = db.Column(db.String(50))
    fatigue_degree = db.Column(db.String(50))
    other_degree = db.Column(db.String(50))
    symptom_id = db.Column(db.Integer,db.ForeignKey('symptoms.id'))

# schemas
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','name','email','tel','country','state','address','age','sign_up_date')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class SymptomSchema(ma.Schema):
    class Meta:
        fields = ('id','cough','resp','fever','fatigue','other','user_id')

symptom_schema = SymptomSchema()
symptoms_schema = SymptomSchema(many=True)

class SpecificSchema(ma.Schema):
    class Meta:
        fields = ('id','cough_degree','fever_degree','fatigue_degree','other_degree','symptom_id')

specific_schema = SpecificSchema()
specifics_schema = SpecificSchema(many=True)