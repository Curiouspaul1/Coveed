from main import db,ma
import datetime as d
from flask import current_app


class User(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200))
    tel = db.Column(db.String(50))
    country = db.Column(db.String(50))
    countryVisited = db.Column(db.String(50))
    state = db.Column(db.String(50))
    address = db.Column(db.String(200))
    travel_history = db.Column(db.Boolean,default=False)
    age = db.Column(db.Integer)
    user_id = db.Column(db.String(100),unique=True)
    sign_up_date = db.Column(db.DateTime())
    sign_up_method = db.Column(db.String(100))
    med_state = db.Column(db.String(50),default="Mild")
    days_left = db.Column(db.Integer)
    symptoms = db.relationship('Symptoms',backref='patient')
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'))
    guide_id = db.Column(db.Integer,db.ForeignKey('guides.id'))
    remarks = db.relationship('Comments',backref='patient')

    def Crt(self):
        # fetch first symptom date
        sdate = self.symptoms[0].date_added 
        t_lapse = sdate + d.timedelta(weeks=2)
        remaining = t_lapse - self.symptoms[-1].date_added
        self.days_left = remaining.days
        
    def set_critical_state(self):
        self.med_state = 'Critical'
        db.session.commit()


    def promoteuser(self):
        self.days_left = 0

    def add_guide(self,data):
        self.guides.append(data)
        db.session.commit()

    def __init__(self,**kwargs):
        super(User, self).__init__(**kwargs)
        self.guides.append(Guides.query.filter_by(id=1).first())
        self.guides.append(Guides.query.filter_by(id=2).first())
        self.guides.append(Guides.query.filter_by(id=3).first())
        if self.role == None and self.email != current_app.config['ADMIN_EMAIL']:
            self.role = Role.query.filter_by(name='USER').first()
        elif self.role == None and self.email == current_app.config['ADMIN_EMAIL']:
            self.role = Role.query.filter_by(name='ADMIN').first()

    #def reset_medstate:
    #self.days_left

#class Vitals(db.Model):


class Symptoms(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True)
    cough = db.Column(db.Boolean,default=False)
    resp = db.Column(db.Boolean,default=False)
    fever = db.Column(db.Boolean,default=False)
    fatigue = db.Column(db.Boolean,default=False)
    other = db.Column(db.String(100))
    date_added = db.Column(db.DateTime())
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    specifics = db.relationship('Specifics',backref='symptom',uselist=False)


class Specifics(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    cough_degree = db.Column(db.String(50))
    fever_degree = db.Column(db.String(50))
    fatigue_degree = db.Column(db.String(50))
    other_degree = db.Column(db.String(50))
    symptom_id = db.Column(db.Integer,db.ForeignKey('symptoms.id'))


class Permission:
    ADD_SYMPTOMS = 1
    CONTACT_HEALTHCARE = 2
    ADMINISTER = 4
    ADMIN = 8


class Role(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    name = db.Column(db.String(20))
    default = db.Column(db.Boolean,default=False,index=True)
    users = db.relationship('User',backref='role')
    docs = db.relationship('Doctor',backref='role')
    permissions = db.Column(db.Integer)

    def __init__(self,**kwargs):
        super(Role,self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def has_permission(self,perm):
        return self.permissions & perm == perm

    def add_permission(self,perm):
        if not self.has_permission(perm):
           self.permissions += perm


    def remove_permission(self,perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0
    
    @staticmethod
    def insert_roles():
        roles = {
            'USER':[Permission.ADD_SYMPTOMS,Permission.CONTACT_HEALTHCARE],
            'DOC' : [Permission.ADMINISTER],
            'ADMIN' : [Permission.ADMIN]
        }

        default = 'USER'
        for r in roles:
            role = Role.query.filter_by(name=r).first()  # check to see if role exists
            if role is None:    # if role doesn't exist already
                role = Role(name=r)     # create role
            role.reset_permission()     # reset role permission
            for perm in roles[r]:       # assign role permission
                role.add_permission(perm)

            role.default = role.name == default # assigns the role as default if its name == the set default role in this method

            db.session.add(role)
        db.session.commit()

# association table
patients = db.Table('patients',
db.Column('user_id', db.Integer,db.ForeignKey('user.id')),
db.Column('guide_id', db.Integer, db.ForeignKey('guides.id'))
)

class Guides(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    name = db.Column(db.String(100))
    done = db.Column(db.Boolean,default=False,index=True)
    info = db.Column(db.PickleType())
    time_lapse = db.Column(db.String(50))
    doc_id = db.Column(db.Integer,db.ForeignKey('doctor.id'))
    patients = db.relationship('User',backref=db.backref('guides'), secondary=patients)

    @staticmethod
    def insert_guides():
        guides = {
            "Pain Medication":['Acetaminophen (Tylenol)','hours=4'],
            "Zinc Supplement":['Cold-Eeze lozenges','hours=4'],
            "Vitamin C":['Vitamin-C','days=1']
        }
        for g in guides:
            guide = Guides.query.filter_by(name=g).first()
            if guide is None:
                guide = Guides(name=g,info=guides[g][0],time_lapse=guides[g][1])
            db.session.add(guide)
        db.session.commit()       

class Doctor(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    doc_id = db.Column(db.String(200),unique=True)
    doc_pass = db.Column(db.String(10),unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    qualification = db.Column(db.String(200))
    docs = db.Column(db.String(500))
    guides = db.relationship('Guides',backref='doctor')
    comments = db.relationship('Comments',backref='doctor')
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'))

    def genId(self):
        d_id = self.first_name[0:3] + '00' + str(Doctor.query.all().index(self)+1)
        self.doc_pass = d_id

    def __init__(self,**kwargs):
        super(Doctor,self).__init__(**kwargs)
        self.role = Role.query.filter_by(name='DOC').first()

class Comments(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    content = db.Column(db.Text())
    date_created = db.Column(db.DateTime())
    doctor_id = db.Column(db.Integer,db.ForeignKey('doctor.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

class Admin(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    admin_id = db.Column(db.String(50),unique=True)
    admin_pass = db.Column(db.String(50),unique=True)

    def genId(self):
        d_id = 'Admin' + '00' + str(len(Admin.query.all())+1)
        self.admin_id = d_id

    def __init__(self,**kwargs):
        super(Admin,self).__init__(**kwargs)
        self.role = Role.query.filter_by(name='ADMIN').first()

