from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User
from flask_login import login_user, logout_user, current_user

auth = Blueprint("auth",__name__)

@auth.route('/signup', methods=["GET","POST"])
def signup():
	if request.method == "POST":
		name = request.form.get("name")
		email = request.form.get("email")
		p1 = request.form.get("pass1")
		p2 = request.form.get("pass2")
		user = User.query.filter_by(email=email).first()
		if user:
			flash("This Account Already Exists! Please Log In instead")
			return redirect(url_for("auth.login"))
		elif len(name)<3:
			flash("Please enter a longer username!")
		elif len(email)<4:
			flash("Please enter your full Email")
		elif p1 != p2:
			flash("Passwords dont match!")
		else:
			try:
				new_user = User(email=email,username=name,password=generate_password_hash(password=p1,method="pbkdf2:sha256"))
				db.session.add(new_user)
				db.session.commit()
				login_user(new_user,remember=True)
				flash("Account Registered!")
			except Exception as e:
				flash("There was an Error..")
		print(name)
	return render_template("signup.html",user=current_user)

@auth.route('/logout')
def logout():
	logout_user()
	flash("Logged Out!")
	return redirect(url_for("auth.login"))

@auth.route('/login', methods=["GET","POST"])
def login():
	if request.method == "POST":
		if current_user.is_authenticated:
			flash(f"You are already logged in as {current_user.username}! Please LogOut to use another account")
			return(render_template("login.html",user=current_user))
		else:
			name = request.form.get("name")
			email = request.form.get("email")
			p1 = request.form.get("pass1")
			user = User.query.filter_by(email=email).first()
			if user:
				if check_password_hash(user.password,p1):
					login_user(user,remember=True)
					flash(f"Succesfully logged in as:{user.username}")
					return redirect(url_for("roads.home"))
				else:
					flash("Incorrect Email ID or Password")
	return render_template("login.html",user=current_user)