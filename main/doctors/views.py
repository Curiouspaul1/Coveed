from . import doctor
from flask import request,make_response,jsonify,current_app,json,session,g,request
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from main.models import User,Doctor,Comments,Guides
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
    resp = jsonify({'pass':doc.doc_pass})
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
            """#token = jwt.encode({'doc_id':doc.doc_id,'exp':d.datetime.utcnow() + d.timedelta(minutes=30)},'secret').decode('utf-8')
            #resp = make_response(jsonify({'login':True}),200)
            #resp.set_cookie('doc-access-token',value=str(token),httponly=True)"""
            uid = doc.doc_id
            return jsonify({"uid":uid}),200
    else:
        return make_response(jsonify({'error':'Invalid id'}),401)
    return make_response(jsonify({'Login':True}),200)

# authorization decor
def login_required(f):
    # wraps around view function (f)
    @wraps(f)
    def function(*args,**kwargs):
        token = None
        if 'doc-access-token' in request.headers:
            #token = request.cookies.get('doc-access-token')
            token = request.headers['doc-access-token']
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
    new_comment.patient = User.query.filter_by(user_id=data['user_id']).first()
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
    users = User.query.filter_by(days_left=0).all()
    print(users)
    resp = jsonify(users_schema.dump(users))

    return resp,200

@doctor.route('/fetchcomments')
@login_required
def fetch_comments(doc):
    comments = doc.comments
    resp = jsonify({'comments':comments_schema.dump(comments)})
    return resp,200

@doctor.route('/fetchcomments/<user_id>')
@login_required
def fetchcomments(doc,user_id):
    comments = doc.comments
    result = []
    for comment in comments:
        if comment.user_id == User.query.filter_by(user_id=user_id).first().id:
            result.append(comment)
    print(comments_schema.dump(result))
    return json.dumps(comments_schema.dump(result)),200

@doctor.route('/flag',methods=['POST'])
@login_required
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
@login_required
def add_prescription(doc):
    data = request.get_json(force=True)
    user = User.query.filter_by(user_id=data['user_id']).first()
    guide = Guides.query.filter_by(name=data['name']).first()
    if guide is None:
        guide = Guides(name=data['name'],info=data['info'][0][1]+'\n'+data['info'][0][1]+'\n'+data['info'][0][2],time_lapse=data['info'][1],doctor=Doctor.query.filter_by(doc_id=doc.id).first())
        db.session.add(guide)
        db.session.commit()
    try:
        user.add_guide(guide)
        return jsonify({'Added Prescription':True}),200
    except Exception as e:
        raise e
        return jsonify({'Added Prescription':False}),500
