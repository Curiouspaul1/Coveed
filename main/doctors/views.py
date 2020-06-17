from . import doctor
from flask import request,make_response,jsonify,current_app,json,session,g,request
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from main.models import User,Doctor,Comments
from main.schema import doc_schema,docs_schema,comment_schema,comments_schema
from firebase_admin import auth
import jwt
from datetime import datetime as d

@doctor.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    

@doctor.route('/add_remark',methods=['POST'])
def comment():
    if 'access-token' in request.headers:
        token = request.headers['access-token']
    user = User.query.filter_by(user_id=auth.verify_id_token(token)['uid'])
    data = request.get_json()
    content = data['comment']
    new_comment = Comments(content=content,date_created=d.utcnow(),patient=user)

    db.session.add(new_comment)
    db.session.commit()

    resp = jsonify({'create_comment':True})

@doctor.route('/delete_remark/<remark_id>',methods=['DELETE'])
def delete_comment(remark_id):
    comment = Comments.query.filter_by(id=remark_id).first()
    db.session.delete(comment)
    db.session.commit()

    resp = jsonify({'Delete':True})

    return resp,200

@doctor.route('/edit_remark/<remark_id>',methods=['PUT'])
def edit_comment():
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

