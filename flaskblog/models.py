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
    date_registered=db.Column(db.DateTime,nullable=False,default=datetime.utcnow())
    #here we use 'Post' instead of 'post', because we are referencing Post class below
    posts=db.relationship('Post',backref='author',lazy=True,cascade="all,delete-orphan")
    comments=db.relationship('Comment',backref='author',lazy=True,cascade="all,delete-orphan")

    #one user can only have one role
    role_id=db.Column(db.Integer,db.ForeignKey('role.id',ondelete='CASCADE'),nullable=False,default=1)

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
        return 'Username: {}, Email: {}, Image: {}, Password: {}, Role: {}'.format(self.username,self.email,self.image_file,self.password,self.role.role)

class Role(db.Model):
    '''
    maybe three roles?
    normal user: create account, create posts, delete its own account
    admin: inherit fro normal user and able to delete user posts,view statistics of website
    super admin: inherit form admin and able to assign user to be admin, downgrade admin to user, change website images

    each user can only be one of three roles, cannot have more than two roles
    one to many relation, one role multiple users



    '''
    id=db.Column(db.Integer,primary_key=True)
    role=db.Column(db.String(15),unique=True,nullable=False)

    is_admin=db.Column(db.Boolean,nullable=False,default=False)
    # can_see_statistic_page=db.Column(db.Boolean,nullable=False,default=False)
    # can_see_admin_page=db.Column(db.Boolean,nullable=False,default=False)
    #should not be able to delete others' account, what if he logged in and you delete it? dont know what kind of errors will pop up
    #delete_normal_account=db.Column(db.Boolean,nullable=False,default=False)
    #delete_admin_account=db.Column(db.Boolean,nullable=False,default=False)

    delete_post=db.Column(db.Boolean,nullable=False,default=False)

    assign_remove_admin=db.Column(db.Boolean,nullable=False,default=False)

    users=db.relationship('User',backref='role',lazy=True,cascade='all,delete')

    def __repr__(self):
        return f'Role:{self.role}, can_see_statistic_page:{self.can_see_statistic_page}, can_see_admin_page=db.Column:{self.can_see_admin_page}, delete_normal_account:{self.delete_normal_account}, delete_admin_account:{self.delete_admin_account}, delete_post:{self.delete_post}, assign_remove_admin:{self.assign_remove_admin}\n'







class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    content=db.Column(db.Text,nullable=False)

    comments=db.relationship('Comment',backref='post',lazy=True,cascade="all,delete-orphan")
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
