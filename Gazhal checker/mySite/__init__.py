from flask import Flask
import secrets, os
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from dotenv import load_dotenv

db = SQLAlchemy()
DBNAME = "mydat.db"

def create():
	app = Flask(__name__)

	load_dotenv()

	if "SECRET_KEY" not in os.environ:
	    with open(".env", "a") as f:
	        key = secrets.token_hex(32)
	        f.write(f"\nSECRET_KEY={key}\n")
	    os.environ["SECRET_KEY"] = key 

	app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
	app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DBNAME}"

	from .roads import roads
	from .auth import auth

	app.register_blueprint(roads)
	app.register_blueprint(auth)

	from .models import User

	login_manager = LoginManager()
	login_manager.init_app(app)
	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

	db.init_app(app)
	create_db(app)
	return app

def create_db(app):
	if not path.exists('instance/'+DBNAME):
		with app.app_context():
			db.create_all()
			print("Db Created")