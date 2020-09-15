import json
from flask import (
    request,render_template,make_response,jsonify,
    current_app,json,session,g
)
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from main.models import User,Symptoms,Specifics,Doctor,Admin
from . import admin
from bcrypt import hashpw,checkpw
import os

@admin.route('/')
def index():
    return render_template('admin_index.html')

@admin.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        resp,status_code = {'status':'Error','message':'No data sent'},400
    password = hashpw(os.getenv('APP_KEY'),data['admin_pass'])
    new_admin = Admin(admin_pass=password)
    db.session.add(new_admin)
    new_admin.genId()
    try:
        db.session.commit()
    except IntegrityError:
        resp,status_code = {'status':'Error','message':'Admin credential already exists'},400

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

@admin.route('/symptoms/<user_id>',methods=['GET'])
def all_symptoms(user_id):
    # fetch user
    try:
        user_id = int(user_id)
        user = User.query.get(user_id)
        symptoms = user.symptoms
        return jsonify(symptoms_schema.dump(symptoms)),200
    except ValueError:
        return {
            'status':'Error',
            'message':f'user id - {user_id} is invalid'
        },400

@admin.route('/doctors/<doctor_id>',methods=['DELETE'])
def removedoc(doctor_id):
    if request.method == 'DELETE':
        # fetch doc object
        try:
            doctor_id = int(doctor_id)
            doc = Doctor.query.get(doctor_id)
            if not doc:
                return {
                    'status':'Error',
                    'message':f'Doctor with id {doctor_id} not found'
                },404
        except ValueError:
            return {
                'status':'Error',
                'message':f'user id - {user_id} is invalid'
            },400
  
@admin.route('/doctors')
def doctors():
    if request.method == 'GET':
        docs = Doctor.query.all()
        return render_template('listdocs.html',docs=docs)


