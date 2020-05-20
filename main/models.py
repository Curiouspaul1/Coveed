from main import db,ma
import datetime as d

class User(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    tel = db.Column(db.String(50))
    country = db.Column(db.String(50))
    state = db.Column(db.String(50))
    address = db.Column(db.String(200))
    age = db.Column(db.Integer)
    username = db.Column(db.String(100),unique=True)
    user_id = db.Column(db.String(100),unique=True)
    sign_up_date = db.Column(db.DateTime(), default=d.datetime.utcnow())
    sign_up_method = db.Column(db.String(100))
    symptoms = db.relationship('Symptoms',backref='patient')
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'))

#class Vitals(db.Model):

class Symptoms(db.Model):
    id = db.Column(db.Integer,nullable=False,primary_key=True)
    cough = db.Column(db.Boolean,default=False)
    resp = db.Column(db.Boolean,default=False)
    fever = db.Column(db.Boolean,default=False)
    fatigue = db.Column(db.Boolean,default=False)
    other = db.Column(db.String(200))
    date_added = db.Column(db.DateTime(), default=d.datetime.utcnow())
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
    ADD_SYMPTOMS = 2
    CONTACT_HEALTHCARE = 5
    ADMINISTER = 7
    ADMIN = 10 

class Role(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    name = db.Column(db.String(20))
    default = db.Column(db.Boolean,default=False,index=True)
    users = db.relationship('User',backref='role')
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

class Guides(db.Model):
    id = db.Column(db.Integer,primary_key=True,nullable=False)
    name = db.Column(db.String(100))
    done = db.Column(db.Boolean,default=False,index=True)
    info = db.Column(db.PickleType())
    time_lapse = db.Column(db.Datetime())

    @staticmethod
    def insert_guides():
        guides = {
            "Pain Medication":['Acetaminophen (Tylenol)',d.timedelta(hours=4)],
            "Zinc Supplement":['Cold-Eeze lozenges',d.timedelta(hours=4)],
            "Vitamin C":['Vitamin-C',d.timedelta(days=1)]
        }
        for g in guides:
            guide = Guides.query.filter_by(name=g).first()
            if guide is None:
                guide = Guides(name=g,info=guides[g])
            db.session.add()
        db.session.commit()
            
# schemas
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','name','email','username','tel','country','state','address','age','sign_up_date','first_name','last_name','user_id')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class SymptomSchema(ma.Schema):
    class Meta:
        fields = ('id','cough','resp','fever','fatigue','other','user_id','date_added')

symptom_schema = SymptomSchema()
symptoms_schema = SymptomSchema(many=True)

class SpecificSchema(ma.Schema):
    class Meta:
        fields = ('id','cough_degree','fever_degree','fatigue_degree','other_degree','symptom_id')

specific_schema = SpecificSchema()
specifics_schema = SpecificSchema(many=True)