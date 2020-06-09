from . import api
import json
from flask import request,make_response,jsonify,current_app,json,session,g,request
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from main.models import User,Symptoms,Specifics
from main.schema import user_schema,users_schema,symptom_schema,symptoms_schema,specific_schema,specifics_schema
from firebase_admin import auth
import firebase_admin
from functools import wraps
import datetime as d
import uuid

@api.route('/login',methods=['POST'])
def login():
    """
    if request.method == 'GET':
        user = User.quer.filter_by(username=username).first()
        if user:
            return make_response(jsonify({"signup_method":user.sign_up_method}),200)
        return make_response("No user with username found",401)
    """
    data = request.get_json()
    if 'access-token' in data:
        token = data['access-token']
        try:
            decoded_token = auth.verify_id_token(token)
        except:
            return make_response(jsonify({'error':'An error occured while trying to decode token'}),500)
        uid = decoded_token['uid']
    # find user with id
    user = User.query.filter_by(user_id=uid).first()
    if user:
        #session['user_id'] = user_id
        return make_response(jsonify({'msg':'verified user successfully'}),200)
    return make_response(jsonify({'error':'no user with such id found'}),400)

def login_required(f):
    @wraps(f)
    def function(*args,**kwargs):
        token = None
        if 'access-token' in request.headers:
            token = request.headers['access-token']
        else:
            return make_response(jsonify({'error':'token not found'}),404)
        try:
            decoded_token = auth.verify_id_token(token)
        except:
            make_response(jsonify({'error':'Unable to validate token'}),500)

        # find user with id
        current_user = User.query.filter_by(user_id=decoded_token['uid']).first()
        return f(current_user,*args,**kwargs)
    return function
        
#@api.before_request
#def before_request():
#g.user = None
#if 'user_id' in session:
#g.user = session['user_id']

# registration route
@api.route('/add_profile',methods=['PUT'])
@login_required
def add_profile(current_user):
    # user data
    payload = request.get_json(force=True)
    user = User.query.filter_by(user_id=current_user.user_id).first()
    email = payload['email']
    tel = payload['tel']
    country = payload['country']
    state = payload['state']
    address = payload['address']
    age = payload['age']

    user.email,user.tel,user.country,user.state,user.address,user.age = email,tel,country,state,address,age
    db.session.commit()

    return make_response(jsonify({"msg":"Profile updated successfully"}),200)

@api.route('/add_symptoms',methods=['POST'])
@login_required
def add_symptoms(current_user):
    data = request.get_json(force=True)
    # fetch user 
    user = User.query.filter_by(user_id=current_user.user_id).first()
    new_data = Symptoms(cough=data[1]['cough'],resp=data[1]['resp'],fever=data[1]['fever'],fatigue=data[1]['fatigue'],other=data[1]['other'],date_added=d.datetime.utcnow())
    new_data.patient = user
    degrees = Specifics(cough_degree=data[2]['coughDegree'],fever_degree=data[2]['feverDegree'],fatigue_degree=data[2]['fatigueDegree'],other_degree=data[2]['otherDegree'],symptom=new_data)
    db.session.add_all([new_data,degrees])
    user.Crt()
    db.session.commit()
    return make_response(jsonify({'msg':'Added symptoms succesfully'}),200)


@api.route('/user_symptoms',methods=['GET'])
@login_required
def user_symptoms(current_user):
    user = User.query.filter_by(user_id=current_user.user_id).first()
    result1 = user.symptoms
    result2 = []
    for i in result1:
        result2.append(specific_schema.dump(Specifics.query.filter_by(symptom_id=i.id).first()))
    return jsonify({"symptoms":symptoms_schema.dump(result1),"specs":result2})
    

@api.route('/signup',methods=['POST'])
def signup():
    data = request.get_json(force=True)
    if 'access-token' in data:
        token = data['access-token']
        decoded_token = auth.verify_id_token(token)
        try:
            new_user = User(first_name=data['firstName'],last_name=data['lastName'],user_id=decoded_token['uid'],sign_up_method=data["signUpMethod"])
            if data['telephone']:
                new_user.tel = data['telephone']
            db.session.add(new_user)
            db.session.commit()
            return make_response(jsonify({"messsage":"Sign up successful"}),200)
        except IntegrityError:
            return make_response(jsonify({"message":"User_id already exists"}),401)

@api.route('/getuser')
@login_required
def getuser(current_user):
    user = User.query.filter_by(user_id=current_user.user_id).first()
    if not user:
        return make_response(jsonify({'msg':'No such user found'}),404)
    return user_schema.jsonify(user)

@api.route('/fetch_user_symptoms')
@login_required
def fetchsymptoms(current_user):
    user = User.query.filter_by(user_id=current_user.user_id).first()
    result = user.symptoms
    return jsonify(symptoms_schema.dump(result)),200