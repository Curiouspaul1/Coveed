import json
from flask import request,make_response,jsonify,current_app,json,session,g
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from main.models import User,Symptoms,Specifics
from . import admin

@admin.route('/delete_users',methods=['DELETE'])
def delete_users():
    users = User.query.all()
    for i in users:
        db.session.delete(i)
        db.session.commit()
    return make_response("Deleted users"),200

@admin.route('/delete_symptoms',methods=['DELETE'])
def delete_symptoms():
    symptoms = Symptoms.query.all()
    for i in symptoms:
        db.session.delete(i)
        db.session.commit()
    return make_response("Cleared symptoms"),200

@admin.route('/users',methods=['GET'])
def all_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))

@admin.route('/symptoms',methods=['GET'])
def all_symptoms():
    symptoms = Symptoms.query.all()
    return jsonify(symptoms_schema.dump(symptoms))
