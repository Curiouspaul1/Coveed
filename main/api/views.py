from . import api
import json
from flask import request,make_response,jsonify,current_app,json,session
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from ..models import User,user_schema,users_schema,Symptoms,symptom_schema,symptoms_schema,Specifics,specific_schema,specifics_schema


@api.route('/login/<username>',methods=['GET','POST'])
def login(username):
    if request.method == 'GET':
        user = User.query.filter_by(username=username).first()
        if user:
            return make_response(jsonify({"signup_method":user.sign_up_method}),200)
        return make_response("No user with username found",401)
    data = request.get_json()
    user_id = data['user_id']
    session['user_id'] = user_id
    if user_id:
        return make_response("Logged in successfully",200)

# registration route
@api.route('/add_profile',methods=['PUT','POST'])
def add_profile():
    user = User.query.filter_by(user_id=session['user_id']).first()
    # user data
    payload = request.get_json(force=True)
    email = payload['email']
    tel = payload['tel']
    country = payload['country']
    state = payload['state']
    address = payload['address']
    age = payload['age']

    user.

    # symptoms
    cough = payload[1]['cough']
    resp = payload[1]['resp']
    fever = payload[1]['fever']
    fatigue = payload[1]['fatigue']
    other = payload[1]['other']

    cough_degree = payload[2]['coughDegree']
    fever_degree = payload[2]['feverDegree']
    fatigue_degree = payload[2]['fatigueDegree']
    other_degree = payload[2]['otherDegree']
    
    symptoms = Symptoms(cough=cough,resp=resp,fever=fever,fatigue=fatigue,other=other)
    #patient = User(email=email,tel=tel,country=country,state=state,address=address,age=age,symptoms=symptoms)
    specifics = Specifics(cough_degree=cough_degree,fever_degree=fever_degree,fatigue_degree=fatigue_degree,other_degree=other_degree,symptom=symptoms)

    db.session.add_all([patient,symptoms,specifics])
    db.session.commit()

    return make_response(user_schema.jsonify(patient),200)

@api.route('/add_symptoms',methods=['POST'])
def add_symptoms():
    data = request.get_json(force=True)
    new_data = Symptoms(cough=data['cough'],resp=data['resp'],fever=data['fever'],fatigue=data['fatigue'],other=data['other'])
    

@api.route('/delete_users',methods=['DELETE'])
def delete_users():
    users = User.query.all()
    for i in users:
        db.session.delete(i)
        db.session.commit()
    return make_response("Deleted users"),200

@api.route('/delete_symptoms',methods=['DELETE'])
def delete_symptoms():
    symptoms = Symptoms.query.all()
    for i in symptoms:
        db.session.delete(i)
        db.session.commit()
    return make_response("Cleared symptoms"),200

@api.route('/users',methods=['GET'])
def all_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))

@api.route('/symptoms',methods=['GET'])
def all_symptoms():
    symptoms = Symptoms.query.all()
    return jsonify(symptoms_schema.dump(symptoms))


@api.route('/user_symptoms/<id>',methods=['GET'])
def user_symptoms(id):
    user = User.query.filter_by(user_id=id).first()
    result = user.symptoms
    return symptom_schema.jsonify(result)

@api.route('/signup',methods=['POST'])
def signup():
    data = request.get_json(force=True)
    username = data['username']
    if username:
        try:
            new_user = User(first_name=data['firstName'],last_name=data['lastName'],username=username,user_id=data['user_id'])
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