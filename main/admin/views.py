from flask import (
    request, render_template, make_response, jsonify
)
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from main.models import User, Symptoms, Doctor, Admin
from main.schema import users_schema, symptoms_schema
from main.auth.auth_helpers import admin_login_required
from . import admin
from bcrypt import hashpw, gensalt


@admin.route('/')
def index():
    return render_template('admin_index.html')


@admin.route('/register', methods=['POST'])
def signup():
    data = request.get_json(force=True)
    pass_ = hashpw(str.encode(data['admin_pass']), gensalt())
    new_admin = Admin(admin_pass=pass_)
    new_admin.genId()
    db.session.add(new_admin)
    try:
        db.session.commit()
        resp, status_code = {
                'status': 'Success',
                'message': 'New Admin created!'
            }, 200
    except IntegrityError:
        resp, status_code = {
            'status': 'Error',
            'message': 'Admin credentials already exist'
        }, 402
    return resp, status_code


@admin.route('/delete_users', methods=['DELETE'])
@admin_login_required
def delete_users(admin):
    users = User.query.all()
    for i in users:
        db.session.delete(i)
        db.session.commit()
    return make_response("Deleted users"), 200


@admin.route('/delete_symptoms', methods=['DELETE'])
@admin_login_required
def delete_symptoms(admin):
    symptoms = Symptoms.query.all()
    for i in symptoms:
        db.session.delete(i)
        db.session.commit()
    return make_response("Cleared symptoms"), 200


@admin.route('/users', methods=['GET'])
@admin_login_required
def all_users(admin):
    users = User.query.all()
    return jsonify(users_schema.dump(users))


@admin.route('/symptoms/<user_id>', methods=['GET'])
@admin_login_required
def all_symptoms(admin, user_id):
    # fetch user
    try:
        user_id = int(user_id)
        user = User.query.get(user_id)
        symptoms = user.symptoms
        return jsonify(symptoms_schema.dump(symptoms)), 200
    except ValueError:
        return {
            'status': 'Error',
            'message': f'user id - {user_id} is invalid'
        }, 400


@admin.route('/doctors/<doctor_id>', methods=['DELETE'])
@admin_login_required
def removedoc(admin, doctor_id):
    if request.method == 'DELETE':
        # fetch doc object
        try:
            doctor_id = int(doctor_id)
            doc = Doctor.query.get(doctor_id)
            if not doc:
                return {
                    'status': 'Error',
                    'message': f'Doctor with id {doctor_id} not found'
                }, 404
        except ValueError:
            return {
                'status': 'Error',
                'message': f'user id - {doctor_id} is invalid'
            }, 400


@admin.route('/doctors')
def doctors():
    if request.method == 'GET':
        docs = Doctor.query.all()
        return render_template('listdocs.html', docs=docs)
