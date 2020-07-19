import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager


app = Flask(__name__)
app.config['MAIL_USERNAME'] = 'yourownemail.com'
app.config['MAIL_PASSWORD'] = 'yourpw'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config["SESSION_COOKIE_HTTPONLY"] = False  # Session Cookie httponly header disabled intentionally to demo cookie hijacking via XSS
app.config["SESSION_COOKIE_SECURE"] = False  # Session Cookie secure header disabled intentionally to demo cookie hijacking via XSS
app.config['X-XSS-Protection'] = 0  # X-XSS Header disabled intentionally to demo XSS
mail = Mail(app)
from flaskshop import routes





















































































































