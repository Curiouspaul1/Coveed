from . import api
import json
from flask import request,make_response,jsonify,current_app,json
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from ..models import User,user_schema,users_schema,Symptoms,symptom_schema,symptoms_schema

# registration route
@api.route('/add_profile',methods=['POST'])
def registeration():
    # user data
    payload = request.get_json()
    name = payload[0]['name']
    email = payload[0]['email']
    tel = payload[0]['tel']
    country = payload[0]['country']
    state = payload[0]['state']
    address = payload[0]['address']
    age = payload[0]['age']

    # symptoms
    cough = payload[1]['cough']
    resp = payload[1]['resp']
    fever = payload[1]['fever']
    fatigue = payload[1]['fatigue']
    other = payload[1]['other']
    
    symptoms = Symptoms(cough=cough,resp=resp,fever=fever,fatigue=fatigue,other=other)
    patient = User(name=name,email=email,tel=tel,country=country,state=state,address=address,age=age,symptoms=symptoms)

    db.session.add_all([patient,symptoms])
    db.session.commit()

    return make_response(user_schema.jsonify(patient),200)

@api.route('/add_symptoms',methods=['POST'])
def add_symptoms():
    data = request.get_json()
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
    user = User.query.filter_by(id=id).first()
    result = user.symptoms
    return symptom_schema.jsonify(result)

@api.route('/signup',methods=['POST'])
def signup():
    data = request.get_json()
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