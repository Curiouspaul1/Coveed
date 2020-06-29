from . import api
from flask import render_template,request,make_response,jsonify,current_app,json,session,g,request
from sqlalchemy.exc import IntegrityError
from main.extensions import db
from flask_cors import cross_origin
from tablib import Dataset
from main.models import User,Symptoms,Specifics,Permission,Doctor
from main.api.email_test import EmergencyMail
from main.schema import user_schema,users_schema,symptom_schema,symptoms_schema,specific_schema,specifics_schema,comments_schema
from firebase_admin import au
import os,uuid,jwt,firebase_admin,json
from functools import wraps
import datetime as d

@api.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    header['Access-Control-Allow-Methods'] = '*'

    return response

@api.route('/login',methods=['POST'])
def login():
    """
    if request.method == 'GET':
        user = User.quer.filter_by(username=username).first()
        if user:
            return make_response(jsonify({"signup_method":user.sign_up_method}),200)
        return make_response("No user with username found",401)
    """
    data = request.get_json()
    if 'access-token' in data:
        token = data['access-token']
        try:
            #decoded_token = auth.verify_id_token(token)
            decoded_token = jwt.decode(token,'secret', algorithms=['HS256'])
        except Exception as e:
            raise e
            return make_response(jsonify({'error':'An error occured while trying to decode token'}),500)
        uid = decoded_token['uid']
    # find user with id
    user = User.query.filter_by(user_id=uid).first()
    if user:
        #session['user_id'] = user_id
        return make_response(jsonify({'msg':'verified user successfully'}),200)
    return make_response(jsonify({'error':'no user with such id found'}),400)

def login_required(f):
    @wraps(f)
    def function(*args,**kwargs):
        token = None
        if 'access-token' in request.headers:
            token = request.headers['access-token']
            #decoded_token = auth.verify_id_token(token)
            decoded_token = jwt.decode(token,'secret', algorithms=['HS256'])
        else:
            return make_response(jsonify({'error':'token not found'}),404)
        uid = decoded_token['uid']
        # find user with id
        current_user = User.query.filter_by(user_id=uid).first()
        return f(current_user,*args,**kwargs)
    return function
        
#@api.before_request
#def before_request():
#g.user = None
#if 'user_id' in session:
#g.user = session['user_id']

# registration route
@api.route('/add_profile',methods=['PUT'])
@login_required
def add_profile(current_user):
    # user data
    payload = request.get_json(force=True)
    user = User.query.filter_by(user_id=current_user.user_id).first()
    email = payload['email']
    tel = payload['tel']
    country = payload['country']
    state = payload['state']
    address = payload['address']
    age = payload['age']

    user.email,user.tel,user.country,user.state,user.address,user.age = email,tel,country,state,address,age
    db.session.commit()

    return make_response(jsonify({"msg":"Profile updated successfully"}),200)

@api.route('/add_symptoms',methods=['POST'])
@login_required
def add_symptoms(current_user):
    if current_user.role.has_permission(Permission.ADD_SYMPTOMS):
        data = request.get_json(force=True)
        # fetch user and create symptoms
        user = User.query.filter_by(user_id=current_user.user_id).first()
        new_data = Symptoms(cough=data[0]['cough'],resp=data[0]['resp'],fever=data[0]['fever'],fatigue=data[0]['fatigue'],other=data[0]['other'],date_added=d.datetime.utcnow())
        new_data.patient = user
        degrees = Specifics(cough_degree=data[1]['coughDegree'],fever_degree=data[1]['feverDegree'],fatigue_degree=data[1]['fatigueDegree'],other_degree=data[1]['otherDegree'],symptom=new_data)
        db.session.add_all([new_data,degrees])
        user.Crt()
        db.session.commit()
        return make_response(jsonify({'msg':'Added symptoms succesfully'}),200)
    else:
        return make_response(jsonify({'error':'You don\'t have permission to do that'}),401)


@api.route('/user_symptoms',methods=['GET'])
@login_required
def user_symptoms(current_user):
    if current_user.role == 'USER':
        user = User.query.filter_by(user_id=current_user.user_id).first()
        result1 = user.symptoms
        result2 = []
        for i in result1:
            result2.append(specific_schema.dump(Specifics.query.filter_by(symptom_id=i.id).first()))
        return jsonify({"symptoms":symptoms_schema.dump(result1),"specs":result2})
    else:
        return make_response(jsonify({'error':'You don\'t have permission to do that'}),401)

    

@api.route('/signup',methods=['POST'])
def signup():
    data = request.get_json(force=True)
    try:
        new_user = User(first_name=data['firstName'],last_name=data['lastName'],sign_up_date=d.datetime.utcnow(),user_id=str(uuid.uuid4()),sign_up_method=data["signUpMethod"])
        if 'telephone' in data.keys():
            new_user.tel = data['telephone']
        else:
            pass
        db.session.add(new_user)
        db.session.commit()
        resp = jsonify({'uid':new_user.user_id})
        return make_response(resp,200)
    except IntegrityError:
        return make_response(jsonify({"message":"User_id already exists"}),401)

@api.route('/getuser')
@login_required
def getuser(current_user):
    user = User.query.filter_by(user_id=current_user.user_id).first()
    if not user:
        return make_response(jsonify({'msg':'No such user found'}),404)
    return user_schema.jsonify(user)

@api.route('/fetch_user_symptoms')
@login_required
def fetchsymptoms(current_user):
    user = User.query.filter_by(user_id=current_user.user_id).first()
    result = user.symptoms
    # write data to json file for graph generation
    import os,json
    data = open(os.path.join(os.getcwd(),'data.json'),'w')
    data.write(json.dumps(symptoms_schema.dump(result)))
    return jsonify(symptoms_schema.dump(result)),200

@api.route('/getremarks')
@login_required
def doc_comments(current_user):
    comments = current_user.remarks
    data = comments_schema.dump(comments)
    for i in data:
        doc = Doctor.query.filter_by(id=i['doctor_id']).first()
        i['first_name'],i['last_name'],i['qualification'] = doc.first_name,doc.last_name,doc.qualification

    resp = jsonify(data)
    return resp,200

# for the sake of cors`preflight requests
def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# testing purposes
@api.route('/promoteuser')
@cross_origin()
@login_required
def promote(current_user):
    if request.method == 'OPTIONS':
        return _build_cors_prelight_response()
    else:
        current_user.promoteuser()
        db.session.commit()
        return jsonify({'Promote':True,'days_left':current_user.days_left}),200

@api.route('/contact_emergency')
@login_required
def emergency(current_user):
    # prepare user info
    user_data = user_schema.dump(User.query.filter_by(id=current_user.id).first())
    User.query.filter_by(id=current_user.id).first().set_critical_state()
    data = Dataset()
    data.headers = ['First Name','Last Name','Email','Address','State','Age','Travel History','Telephone']
    for i in [(user_data['first_name'],user_data['last_name'],user_data['email'],user_data['address'],user_data['state'],user_data['age'],user_data['travel_history'],user_data['tel'])]:
        data.append(i)
    with open(f'{os.getcwd()}/user_dat.xlsx','wb') as file:
        print(file.name)
        file.write(data.export('xlsx'))
        # actually send the message
        try:
            result = EmergencyMail("Emergency Report!",render_template('Emergency.html'),file.name)
            if result:
                return jsonify({'Sent Email':True}),200
            else:
                return jsonify({'Email not sent':True}),500  
        except Exception as e:
            raise e
            return jsonify({'Sent Email':False}),500
        file.close()

    
