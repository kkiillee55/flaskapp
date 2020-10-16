from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from flask_login import current_user
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField,IntegerField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    #username non-empty length 2-20
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired(),])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])

    submit=SubmitField('Sign Up')


    '''
    to see if username already in database
    the naming convention is validate_<filedname>
    here fieldnames are username,email,password,confirm_password
    we need to validate username and email, so we got
    def validate_username(param_user) param_user is from form.username, that's why ne use param_user.data
    def validate_email(param_email) param_email is from form.email, use param_email.data
    
    '''
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken, Choose another one')

    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email already exists")

class LoginForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember me')
    submit=SubmitField('Log in')

class UpdateAccountForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    picture=FileField('Profile picture',validators=[FileAllowed(['jpg','png','jpeg'])])


    submit=SubmitField('Update')

    def validate_username(self,username):
        if username.data!=current_user.username:
            user=User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken')

    def validate_email(self,email):
        if email.data!=current_user.email:
            user=User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email has been taken')



class PostForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content=TextAreaField('Content',validators=[DataRequired()])
    submit=SubmitField('Post!')

class RequestResetForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email()])
    submit=SubmitField('Request Password Reset')
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('No Such Email, register first')

class ResetPasswordForm(FlaskForm):
    password=PasswordField('New Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm New Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Reset Password')

#curretnly not in use
class PageForm(FlaskForm):
    page_id=IntegerField('Page_id',validators=[DataRequired()])
    submit=SubmitField('Go')

class CommentForm(FlaskForm):
    #replyto=StringField('Reply to',validators=[DataRequired()])
    content=StringField('Content',validators=[DataRequired()])
    submit=SubmitField('Submit')