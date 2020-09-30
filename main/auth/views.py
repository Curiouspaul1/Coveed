from . import auth
from main.models import Doctor, Admin
from flask import request, make_response, jsonify, redirect, url_for, session
from .auth_helpers import check_doc_id
import os, jwt, uuid
import datetime as d
from bcrypt import checkpw
from uuid import UUID
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

g = False

# DOctor Auth ##


@auth.route('/doctor', methods=['POST'])
def login():
    cred = request.get_json()
    if check_doc_id(cred['doc_pass']):
        doc = Doctor.query.filter_by(doc_pass=cred['doc_pass']).first()
        if not doc:
            return make_response(
                {'error': 'Doc with id not found'}
            ), 404
        else:
            # Xss Tokens
            key = os.environ['APP_KEY']
            access_token = jwt.encode(
                {
                    'doc_id': doc.doc_id,
                    'exp': d.datetime.utcnow() + d.timedelta(minutes=60)
                }, key
            )
            refresh_token = jwt.encode(
                {
                    'doc_id': doc.doc_id,
                    'exp': d.datetime.utcnow()+d.timedelta(days=30)
                }, key
            )
            # CSRF Tokens
            uid = str(uuid.uuid4())
            csrf_access_token = jwt.encode(
                {
                    'uid': uid,
                    'exp': d.datetime.utcnow()+d.timedelta(minutes=60)
                }, key
            ).decode('utf-8')
            csrf_refresh_token = jwt.encode(
                {
                    'uid': uid, 'exp': d.datetime.utcnow()+d.timedelta(days=30)
                }, key
            ).decode('utf-8')
            print(csrf_access_token, csrf_refresh_token)
            resp = make_response(
                {
                    'login': True, 'dc_token': str(csrf_access_token),
                    'dc_refresh_token': str(csrf_refresh_token)
                }
            ), 200
            # XSS Cookies
            resp.set_cookie(
                'doc_access_token', value=access_token, httponly=True,
                samesite='None', secure=True
            )
            resp.set_cookie(
                'doc_refresh_token', value=refresh_token, httponly=True,
                samesite='None', secure=True
            )
            # CSRF Cookies
            return resp
    else:
        return make_response(jsonify({'error': 'Invalid id'}), 401)


@auth.route('/doctor/refresh_token', methods=['POST'])
def refresh_token():
    if request.cookies.get('doc_refresh_token') and request.headers['doc_csrf_refresh_token']:
        d_token, dc_token = request.cookies.get('doc_refresh_token'),
        request.headers['doc_csrf_refresh_token']
        # try to decode
        try:
            token_data = jwt.decode(d_token, os.environ['APP_KEY'])['doc_id']
            refresh_token_data = jwt.decode(
                dc_token,
                os.environ['APP_KEY']
            )['uid']
        except InvalidSignatureError or ExpiredSignatureError:
            resp, status_code = {"error": "Problem decoding token"}, 500

        new_access_token = jwt.encode(
            {
                'doc_id': token_data,
                'exp': d.datetime.utcnow() + d.timedelta(minutes=60)
            }, os.environ['APP_KEY']
        ).decode('utf-8')
        # validate csrf token
        if isinstance(UUID(refresh_token_data), type(uuid.uuid4())):
            uid = str(uuid.uuid4())
            new_csrf_token = jwt.encode(
                {
                    'uid': uid,
                    'exp': d.datetime.utcnow() + d.timedelta(minutes=60)
                }, os.environ['APP_KEY']
            ).decode('utf-8')
            resp = make_response(
                {
                    'refresh': 'successful',
                    'dc_token': new_csrf_token
                }
            )

            resp.set_cookie(
                'doc_access_token', value=new_access_token,
                httponly=True
            )
            return resp
        else:
            return {'error': 'Invalid Token'}, 401
    else:
        resp, status_code = {'Error': 'Token missing'}, 404
    return resp, status_code


#  Admin Auth ########
@auth.route('/admin', methods=['POST'])
def admin():
    # fetch credentials
    _id = request.form['_id']
    _pass = request.form['_pass']
    if not _id or not _pass:
        resp, status_code = {
            'status': 'Error',
            'message': 'Credentials missing please fill form properly'
        }, 404
    else:
        # find admin with credentials
        admin = Admin.query.filter_by(admin_id=_id).first()
        if not admin:
            resp, status_code = {
                'status': 'Error',
                'message': f'user with id {_id}'
            }, 404
        else:
            pass_ = admin.admin_pass
            # compare password hashes
            if checkpw(str.encode(_pass), pass_):
                # Xss Tokens
                key = os.environ['APP_KEY']
                access_token = jwt.encode(
                    {
                        'admin_id': admin.admin_id,
                        'exp': d.datetime.utcnow() + d.timedelta(minutes=60)
                    }, key
                )
                refresh_token = jwt.encode(
                    {
                        'admin_id': admin.admin_id,
                        'exp': d.datetime.utcnow()+d.timedelta(days=30)
                    }, key
                )
                session['access_token'] = access_token
                session['refresh_token'] = refresh_token
                resp, status_code = redirect(url_for('admin.all_users')), 200
            else:
                resp, status_code = {
                    'status': 'Error',
                    'message': 'Incorrect password'
                }, 400
    return resp, status_code
