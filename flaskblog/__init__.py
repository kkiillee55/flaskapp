from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os
import json

with open('flaskblog/secrets.json') as fp:
    secrets=json.load(fp)
#print(secrets)

app=Flask(__name__)
app.config['SECRET_KEY']=secrets['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI']=secrets['SQLALCHEMY_DATABASE_URI']
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
app.config['MAIL_USERNAME']=secrets['MAIL_USERNAME']
app.config['MAIL_PASSWORD']=secrets['MAIL_PASSWORD']
mail=Mail(app)

#because we have @app.route in routes.py,
from flaskblog import routes
