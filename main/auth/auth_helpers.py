from flask import request,make_response,jsonify
from main.models import Doctor
from firebase_admin import auth
from functools import wraps
import re,os


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
        return f(current_user,*args,**kwargs)
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
    def function(*args,**kwargs):
        token = None
        print(request.cookies.get('doc_access_token'))
        print( request.headers.get('doc_csrf_access_token'))
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
            except Exception as e:
                raise e
                status_code,resp = 500,{'status':'Error','message':'Problem Decoding Token'}
        else:
            status_code,resp = 404,{'status':'Error','message':'Token Missing'}
        return resp,status_code
    return function