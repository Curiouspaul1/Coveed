from main import db
from main.models import User, Role

import pytest

'''
def test_api_route(test_client):
    db.create_all()

    Role.insert_roles()
    assert Role.query.all()[0].name == 'USER'

    response = test_client.get('/api/index')
    assert response.status_code == 200

user = User(
        first_name='Paul', last_name='Asalu', email='asp@gmail.com',
        tel='09045444444', country='Nigeria', state='Lagos',
        address='66 Baruwa Street, Abgoju', travel_history=0,
        age=22, user_id='1234', med_state='Mild', days_left=1)
    
    
    db.session.add(user)
    db.session.commit()

    assert user.first_name == 'Paul'
'''