from flask import request, make_response, jsonify, session
from main.models import Doctor, Admin
from firebase_admin import auth
from functools import wraps
import re, os,jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

########## Patient Auth Helper ##########

def login_required(f):
    """
    Checks that current user is logged in before request
    github : <github.com/Curiouspaul1>
    author : Curiouspaul
    """
    @wraps(f)
    def function(*args,**kwargs):
        print(request.headers)
        token = None
        if 'access-token' in request.headers:
            token = request.headers['access-token']
            print(token)
            decoded_token = auth.verify_id_token(token)
            #decoded_token = jwt.decode(token,'secret', algorithms=['HS256'])
        else:
            return make_response(jsonify({'error':'token not found'}),404)
        uid = decoded_token['uid']
        # find user with id
        current_user = User.query.filter_by(user_id=uid).first()
        if not current_user:
            return jsonify({'Error':'User not found'}),404
        return f(current_user, *args, **kwargs)
    return function

############ Doctor Auth Helpers ###############

def check_doc_id(d_id):
    """regex validates doc-pass"""
    exp = re.compile(r'([a-zA-Z]{3})(\d\d\d)')

    if exp.search(d_id):
        return True
    else:
        return False

def doc_login_required(f):
    """
    Checks that doctor is logged in before request
    github : <github.com/Curiouspaul1>
    author : Curiouspaul
    """
    @wraps(f)
    def function(*args, **kwargs):
        token = None
        if 'doc_access_token' in request.cookies and 'doc_csrf_access_token' in request.headers:
            token = request.cookies.get('doc_access_token')
            print(token)
            try:
                token = jwt.decode(token,os.environ['APP_KEY'])
                # find doc
                doc = Doctor.query.filter_by(doc_id=token['doc_id']).first()
                if doc:
                    return f(doc,*args,**kwargs)
                else:
                    status_code,resp = 404,{'status':'Error','message':'Doc with matching ID not found'}
            except ExpiredSignatureError:
                status_code,resp = 400,{'status':'Error','message':'Token is expired!'}
            else:
                status_code,resp = 500,{'status':'Error','message':'Problem decoding token'}
        else:
            status_code,resp = 404,{'status':'Error','message':'Token Missing'}
        return resp,status_code
    return function

############ Admin Auth Helpers ###############

def check_admin_id(d_id):
    """regex validates admin_id"""
    exp = re.compile(r'([a-zA-z]{3})(\d\d\d)')

    if exp.search(d_id):
        return True
    else:
        return False

def admin_login_required(f):
    """
    Checks that admin is logged in before request
    github : <github.com/Curiouspaul1>
    author : Curiouspaul
    """
    @wraps(f)
    def function(*args, **kwargs):
        token=None
        print(session['access_token'])
        if 'admin_access_token' in request.cookies and 'admin_csrf_access_token' in request.headers:
            token = request.cookies.get('admin_access_token')
            try:
                token = jwt.decode(token, os.environ['APP_KEY'])
                #find admin
                admin = Admin.query.filter_by(admin_id=token['admin_id']).first()
                if not admin:
                    resp,status_code = {'status':'Error','message':'Admin with token payload not found'},404
                return f(admin,*args,**kwargs)
            except ExpiredSignatureError:
                status_code,resp = 400,{'status':'Error','message':'Token is expired!'}
            else:
                status_code,resp = 500,{'status':'Error','message':'Problem decoding token'}
        else:
            resp,status_code = {'status':'Error','message':'Token is missing'},404
        return resp,status_code
    return function

