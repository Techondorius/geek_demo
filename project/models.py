from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.String(100), unique=True)
    manaba_id = db.Column(db.String(10), default='default', nullable=False)
    manaba_pass = db.Column(db.String(100), default='default', nullable=False)


class test_list(db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    task_name = db.Column(db.String(100))
    deadline = db.Column(db.DateTime)
