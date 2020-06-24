from . import doctor
from flask import request,make_response,jsonify,current_app,json,session,g,request
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from main.models import User,Doctor,Comments
from main.schema import users_schema,doc_schema,docs_schema,comment_schema,comments_schema
from firebase_admin import auth
import jwt
import datetime as d
import re
import uuid
from functools import wraps

@doctor.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    doc = Doctor(first_name=data['first_name'],last_name=data['last_name'],doc_id=str(uuid.uuid4()),qualification=data['qualification'])
    db.session.add(doc)
    doc.genId()
    db.session.commit()
    resp = jsonify({'register':True})
    return resp,200

# regex validates doc-pass
def check_doc_id(d_id):
    exp = re.compile(r'([a-zA-Z]{3})(\d\d\d)')

    if exp.search(d_id):
        return True
    else:
        return False
    

@doctor.route('/login',methods=['POST'])
def login():
    cred = request.get_json()
    if check_doc_id(cred['doc_pass']):
        doc = Doctor.query.filter_by(doc_pass=cred['doc_pass']).first()
        if not doc:
            return make_response(jsonify({'error':'Doc with id not found'}),404)
        else:
            token = jwt.encode({'doc_id':doc.doc_id,'exp':d.datetime.utcnow() + d.timedelta(minutes=30)},'secret').decode('utf-8')
            resp = make_response(jsonify({'login':True}),200)
            resp.set_cookie('doc-access-token',value=str(token),httponly=True)
            return make_response(jsonify({'Login':True}),200)
    else:
        return make_response(jsonify({'error':'Invalid id'}),401)

# authorization decor
def login_required(f):
    # wraps around view function (f)
    @wraps(f)
    def function(*args,**kwargs):
        token = None
        if 'doc-access-token' in request.cookies:
            token = request.cookies.get('doc-access-token')
            print(token)
            try:
                token = jwt.decode(token,'secret')
                # find doc
                doc = Doctor.query.filter_by(doc_id=token['uid']).first()
                if doc:
                    return f(doc,*args,**kwargs)
                else:
                    return make_response(jsonify({'Error':'Doc with matching id not found'}),404)
            except Exception as e:
                raise e
                return make_response(jsonify({"error":"Problem decoding token"}),500)
        else:
            return make_response(jsonify({'Token':'Missing'}),401)
    return function

@doctor.route('/add_remark',methods=['POST'])
@login_required
def comment(doc):
    data = request.get_json()
    content = data['comment']
    new_comment = Comments(content=content,doctor=doc,date_created=d.datetime.utcnow())
    if 'access-token' in request.headers:
        token = request.headers['access-token']
        new_comment.patient = User.query.filter_by(user_id=jwt.decode(token,'secret')['uid']).first()
    db.session.add(new_comment)
    db.session.commit()
    resp = jsonify({'create_comment':True})
    return resp,200

@doctor.route('/delete_remark/<remark_id>',methods=['DELETE'])
@login_required
def delete_comment(doc,remark_id):
    comment = Comments.query.filter_by(id=remark_id).first()
    db.session.delete(comment)
    db.session.commit()

    resp = jsonify({'Delete':True})

    return resp,200

@doctor.route('/edit_remark/<remark_id>',methods=['PUT'])
@login_required
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
@login_required
def getpatients(doc):
    users = User.query.all()
    patients = []
    for user in users:
        if user.days_left == 0:
            patients.append(user)
    resp = jsonify(users_schema.dump(patients))

    return resp,200
    
