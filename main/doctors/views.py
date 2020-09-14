from . import doctor
from flask import request,make_response,jsonify,current_app,json,session,g,request
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from main.models import User,Doctor,Comments,Guides
from main.schema import users_schema,doc_schema,docs_schema,comment_schema,comments_schema
from main.auth.auth_helpers import check_doc_id,doc_login_required
from firebase_admin import auth
from jwt.exceptions import InvalidSignatureError,ExpiredSignatureError
from flask_cors import cross_origin
import jwt
import datetime as d
import re,os
import uuid
from uuid import UUID


@doctor.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    doc = Doctor(first_name=data['first_name'],last_name=data['last_name'],doc_id=str(uuid.uuid4()),qualification=data['qualification'])
    db.session.add(doc)
    doc.genId()
    db.session.commit()
    resp = jsonify({'pass':doc.doc_pass})
    return resp,200
    

@doctor.route('/add_remark',methods=['POST'])
@doc_login_required
def comment(doc):
    data = request.get_json()
    if not data:
        resp = {'status':'Error','message':'No data sent!'}
        status_code = 400
    else:
        content = data['comment']
        new_comment = Comments(content=content,doctor=doc,date_created=d.datetime.utcnow())
        new_comment.patient = User.query.filter_by(user_id=data['user_id']).first()
        db.session.add(new_comment)
        db.session.commit()
        resp,status_code = {'status':'Success','message':'Added Remark Successfully'},200
    return resp,status_code

@doctor.route('/delete_remark/<remark_id>',methods=['DELETE'])
#@cross_origin(allow_headers=['Access-Control-Allow-Credentials'])
@doc_login_required
def delete_comment(doc,remark_id):
    comment = Comments.query.filter_by(id=remark_id).first()
    db.session.delete(comment)
    db.session.commit()

    resp = jsonify({'Delete':True})

    return resp,200

@doctor.route('/edit_remark/<remark_id>',methods=['PUT'])
#@cross_origin(allow_headers=['Access-Control-Allow-Credentials'])
@doc_login_required
def edit_comment(doc,remark_id):
    data = request.get_json()
    # fetch comment
    comment = Comments.query.filter_by(id=remark_id).first()
    comment.content = data['comment']
    try:
        db.session.commit()
    except Exception as e:
        raise e
        return make_response(jsonify({'Edit':False}),500)
    return make_response(jsonify({'Edit':True}),200)

@doctor.route('/getpatients')
#@cross_origin(allow_headers=['Access-Control-Allow-Credentials'])
@doc_login_required
def getpatients(doc):
    users = User.query.filter_by(days_left=0).all()
    print(users)
    resp = jsonify(users_schema.dump(users))

    return resp,200

@doctor.route('/fetchcomments')
#@cross_origin(allow_headers=['Access-Control-Allow-Credentials'])
@doc_login_required
def fetch_comments(doc):
    comments = doc.comments
    resp = jsonify({'comments':comments_schema.dump(comments)})
    return resp,200

@doctor.route('/fetchcomments/<user_id>')
@doc_login_required
def fetchcomments(doc,user_id):
    comments = doc.comments
    result = []
    for comment in comments:
        if comment.user_id == User.query.filter_by(user_id=user_id).first().id:
            result.append(comment)
    print(comments_schema.dump(result))
    return json.dumps(comments_schema.dump(result)),200

@doctor.route('/flag',methods=['POST'])
#@cross_origin(allow_headers=['Access-Control-Allow-Credentials'])
@doc_login_required
def flagcase(doc):
    data = request.get_json()
    # find user
    user = User.query.filter_by(user_id=data['user_id']).first()
    try:
        user.set_critical_state()
        return jsonify({'Flagged Critical':True}),200
    except Exception as e:
        return jsonify({'Error':'An error occurred'}),500

@doctor.route('/add_prescription',methods=['POST'])
#@cross_origin(allow_headers=['Access-Control-Allow-Credentials'])
@doc_login_required
def add_prescription(doc):
    data = request.get_json(force=True)
    user = User.query.filter_by(user_id=data['user_id']).first()
    guide = Guides.query.filter_by(name=data['name']).first()
    if guide is None:
        guide = Guides(name=data['name'],info=data['info'][0][1]+'\n'+data['info'][0][1]+'\n'+data['info'][0][2],time_lapse=data['info'][1],doctor=doc)
        db.session.add(guide)
        db.session.commit()
    try:
        user.add_guide(guide)
        return jsonify({'Added Prescription':True}),200
    except Exception as e:
        raise e
        return jsonify({'Added Prescription':False}),500
