import pytest
from main import __call__, db
from main.models import (
    User, Role, Guides, Doctor, Symptoms, Comments
)
import datetime as d


def test_role(test_client):
    db.create_all()

    # User
    roles = Role.insert_roles()
    assert Role.query.all()[0].name == 'USER'
    assert Role.query.all()[0].default == True
    assert Role.query.all()[0].permissions == 3

    perm = Role.query.all()[0].has_permission(3)
    assert Role.query.all()[0].permissions & perm == perm
    
    Role.query.all()[0].add_permission(4)
    assert Role.query.all()[0].permissions == 7
    
    Role.query.all()[0].remove_permission(3)
    assert Role.query.all()[0].permissions == 4

    Role.query.all()[0].reset_permission()
    assert Role.query.all()[0].permissions == 0


def test_guides(test_client):

    Guides.insert_guides()
    guides = Guides.query.all()

    assert guides[0].name == 'Pain Medication'
    assert guides[0].done == False
    assert guides[0].info == 'Acetaminophen (Tylenol)'
    assert guides[0].time_lapse == 'hours=4'


def test_doctor(test_client):

    doctor = Doctor(
        first_name='Tunji', last_name='Bashorun',
        qualification='MBBS', docs='my docs'
    )

    doctor.genId()

    roles = Role.insert_roles()
    role = Role.query.filter_by(name='DOC').first()
    role.role = role
    
    assert doctor.first_name == 'Tunji'
    assert doctor.last_name == 'Bashorun'
    assert doctor.qualification == 'MBBS'
    assert doctor.docs == 'my docs'
    assert doctor.role.name == 'DOC'



def test_symptoms(test_client):
    symptoms = Symptoms(
        other='Undefined', date_added='1'
    )

    symptoms.cough == False
    symptoms.resp == False
    symptoms.fever == False
    symptoms.fatigue == False
    symptoms.other == 'Undefined'
    symptoms.date_added == '1'


def test_comments(test_client):
    comments = Comments(
        content='Doing Well', date_created='1'
    )

    assert comments.content == 'Doing Well'
    assert comments.date_created =='1'

    #db.drop_all()


def test_new_user(test_client):
    db.create_all()
    user = User(
        first_name='Paul', last_name='Asalu', email='asp@gmail.com',
        tel='09045444444', country='Nigeria', state='Lagos',
        address='66 Baruwa Street, Agboju',
        age=22, user_id='1234', sign_up_date=d.datetime.utcnow(),
        sign_up_method='Firebase', days_left=1
    )
    
    Role.insert_roles()
    role = Role.query.filter_by(id=1).first()
    user.role = role

    Guides.insert_guides()
    guide = Guides.query.filter_by(id=1).first()
    user.guides.append(guide)
   
    db.session.add(user)
    db.session.commit()

    assert user.first_name == 'Paul'
    assert user.last_name == 'Asalu'
    assert user.email == 'asp@gmail.com'
    assert user.tel == '09045444444'
    assert user.country == 'Nigeria'
    assert user.state == 'Lagos'
    assert user.address == '66 Baruwa Street, Agboju'
    assert user.travel_history == 0
    assert user.age == 22
    assert user.user_id == '1234'
    assert user.sign_up_date == user.sign_up_date
    assert user.sign_up_method == 'Firebase'
    assert user.med_state == 'Mild'
    assert user.days_left == 1
    assert user.role.name == 'USER'

    db.drop_all()