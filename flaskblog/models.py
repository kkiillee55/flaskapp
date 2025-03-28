from datetime import datetime
from flaskblog import db,login_manager,app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    image_file=db.Column(db.String(20),nullable=False,default='default.jpg')
    password=db.Column(db.String(60),nullable=False)
    #here we use 'Post' instead of 'post', because we are referencing Post class below
    posts=db.relationship('Post',backref='author',lazy=True)
    comments=db.relationship('Comment',backref='author',lazy=True)

    def get_reset_token(self,expires_sec=1800):
        s=Serializer(app.config['SECRET_KEY'],expires_sec)
        #token=s.dumps({'user_id':self.id}).decode('utf-8')
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s=Serializer(app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return 'Username: {}, Email: {}, Image: {}, Password: {}'.format(self.username,self.email,self.image_file,self.password)

class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    content=db.Column(db.Text,nullable=False)

    comments=db.relationship('Comment',backref='post',lazy=True,cascade="all,delete")
    #here we use 'user.id' instead of 'User.id', because we are referencing the table name in database,
    #database will convert capital letters to lowercase letters, so we will have user table instead of User table
    #feels a bit inconsistancy...
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    def __repr__(self):
        return 'Title:{}, Date:{}, Author:{}\n'.format(self.title,self.date_posted,self.author.username)

class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date_commented=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    replyto=db.Column(db.String(20),unique=False,nullable=False)
    content=db.Column(db.Text,nullable=False)

    post_id=db.Column(db.Integer,db.ForeignKey('post.id',ondelete='CASCADE'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'),nullable=False)
    def __repr__(self):
        return 'To:{}: {}, by:{}'.format(self.replyto,self.content,self.author.username)