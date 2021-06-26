import os
import json

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, ARRAY, inspect
from sqlalchemy.sql.sqltypes import DateTime
from flask_sqlalchemy import SQLAlchemy

DB_HOST = os.getenv('DB_HOST', '0.0.0.0:5433')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')  
DB_NAME = os.getenv('DB_NAME', 'volunteer_app')  
DB_PATH = 'postgresql+psycopg2://{}:{}@{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

class ModelMixin(object):
    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=DB_PATH):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    return db

'''
event_users association table
    each user can have multiple events and vice-versa 
'''
event_users = db.Table('event_users', 
    Column('event_id', Integer, ForeignKey('event.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True)
)
    
'''
Organisation
    entity that can create events 
'''
class Organisation(ModelMixin, db.Model):  
    __tablename__ = 'organisation'

    id = Column(Integer, primary_key=True)
    auth0_id = Column(String, unique=True)
    name = Column(String, nullable=False)
    description = Column(String)
    website = Column(String)
    phone_contact = Column(String)
    email_contact = Column(String)

    #an organisation can create multiple events
    events = db.relationship('Event', lazy=True, 
        backref=db.backref('organisation', lazy='joined'))
    
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'phone_contact': self.phone_contact,
            'email_contact': self.email_contact,
        }
'''
Event
    a volunteering / charity event 
'''
class Event(ModelMixin, db.Model):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    address = Column(String)

    
    #tags / interests / category? 
    #required_skills?

    #number of volunteers required?

    #event is child of organisation 
    organisation_id = Column(Integer, ForeignKey('organisation.id'), nullable=False)

    #events and users: many-to-many
    participants = db.relationship('User', secondary=event_users,
        backref=db.backref('events', lazy="joined"))

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'address': self.address,
            'organisation_id': self.organisation_id,
            'organisation': {
                'id': self.organisation_id,
                'name': self.organisation.name,
            },
            'participants': [{
                'id': user.id,
                'name': user.name
            } for user in self.participants]
        }    
'''
User
    entity that can participate in events
'''
class User(ModelMixin, db.Model):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    auth0_id = Column(String, unique=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    email_contact = Column(String)
    phone_contact = Column(String)

    join_date = Column(DateTime)
    skills = Column(ARRAY(String))

    #interests?
    #skills?

