from . import db
from flask_login import UserMixin
from sqlalchemy import func

class User(db.Model, UserMixin):
	id = db.Column(db.Integer,primary_key=True)
	email = db.Column(db.String(255),unique=True, index=True)
	username = db.Column(db.String(40),unique=True, index=True)
	password = db.Column(db.String(1000))
	messages = db.relationship('Message', back_populates='user', lazy=True)

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	userid = db.Column(db.Integer, db.ForeignKey('user.id'))
	content = db.Column(db.Text(2000))
	date = db.Column(db.DateTime(timezone=True),default=func.now())
	user = db.relationship('User', back_populates='messages')