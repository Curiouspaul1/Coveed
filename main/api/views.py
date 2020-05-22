from . import api
import json
from flask import request,make_response,jsonify,current_app,json,session,g
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from main.models import User,Symptoms,Specifics
from main.schema import user_schema,users_schema,symptom_schema,symptoms_schema,specific_schema,specifics_schema
from functools import wraps
import datetime as d

@api.route('/login/<username>',methods=['GET','POST'])
def login(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user:
            return make_response(jsonify({"signup_method":user.sign_up_method}),200)
        return make_response("No user with username found",401)
    data = request.get_json()
    user_id = data['user_id']
    # find user with id
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        session['user_id'] = user_id
        return make_response("Logged in successfully",200)
    return make_response(jsonify({'error':'no user with such id found'}),400)

"""def login_required(f):
    @wraps(f)
    def function(*args,**kwargs):
        user_id = None
        if session['user_id']:
            user_id = session['user_id']
        else:
            return make_response(jsonify({"error":"Please Login to continue"}),400)
        current_user = User.query.filter_by(user_id=user_id).first()
        return f(current_user,*args,**kwargs)
    return function"""
        
#@api.before_request
#def before_request():
#g.user = None
#if 'user_id' in session:
#g.user = session['user_id']

# registration route
@api.route('/add_profile',methods=['PUT'])
def add_profile():
    # user data
    payload = request.get_json(force=True)
    user = User.query.filter_by(user_id=payload['user_id']).first()
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
def add_symptoms():
    data = request.get_json(force=True)
    # fetch user 
    user = User.query.filter_by(user_id=data[0]['user_id']).first()
    new_data = Symptoms(cough=data[1]['cough'],resp=data[1]['resp'],fever=data[1]['fever'],fatigue=data[1]['fatigue'],other=data[1]['other'],date_added=d.datetime.utcnow())
    new_data.patient = user
    degrees = Specifics(cough_degree=data[2]['coughDegree'],fever_degree=data[2]['feverDegree'],fatigue_degree=data[2]['fatigueDegree'],other_degree=data[2]['otherDegree'],symptom=new_data)
    db.session.add_all([new_data,degrees])
    user.Crt()
    db.session.commit()
    return make_response(jsonify({'msg':'Added symptoms succesfully'}),200)


@api.route('/user_symptoms/<id>',methods=['GET'])
def user_symptoms(id):
    user = User.query.filter_by(user_id=id).first()
    result1 = user.symptoms
    result2 = []
    for i in result1:
        result2.append(specific_schema.dump(Specifics.query.filter_by(symptom_id=i.id).first()))
    return jsonify({"symptoms":symptoms_schema.dump(result1),"specs":result2})
    

@api.route('/signup',methods=['POST'])
def signup():
    data = request.get_json(force=True)
    username = data['username']
    if username:
        try:
            new_user = User(first_name=data['firstName'],last_name=data['lastName'],username=username,user_id=data['user_id'],sign_up_method=data["signUpMethod"])
            if data['email']:
                new_user.email = data['email']
            elif data['telephone']:
                new_user.tel = data['telephone']
            db.session.add(new_user)
            db.session.commit()
            return make_response(jsonify({"messsage":"Sign up successful"}),200)
        except IntegrityError:
            return make_response(jsonify({"message":"Username already exists"}),401)
    return make_response("Invalid Entry, no username was sent",401)

@api.route('/getuser/<user_id>')
def getuser(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return make_response(jsonify({'msg':'No such user found'}),404)
    return user_schema.jsonify(user)

@api.route('/fetch_user_symptoms/<user_id>')
def fetchsymptoms(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    result = user.symptoms
    return jsonify(symptoms_schema.dump(result)),200