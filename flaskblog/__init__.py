from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os
app=Flask(__name__)
app.config['SECRET_KEY']='21e4d270a08ee35c7bac3a3e9f5f29da'
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:12345678@localhost:3306/flask'
db=SQLAlchemy(app)
migrate=Migrate(app,db)
manager=Manager(app)
manager.add_command('db',MigrateCommand)

bcrypt=Bcrypt(app)
login_manager=LoginManager(app)

#when we are logged out, user cannot go to /account
#this help help redirect to /login when user is trying to access /account when logged out
login_manager.login_view='login'
login_manager.login_message_category='info'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']='zhangliao322@gmail.com'
app.config['MAIL_PASSWORD']='rtyzkwcwlcmcxoew'
mail=Mail(app)

#because we have @app.route in routes.py,
from flaskblog import routes
