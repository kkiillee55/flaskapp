from flask import url_for,render_template,flash,redirect,request,abort
from flaskblog import app,bcrypt,db,mail
from flaskblog.forms import RegistrationForm,LoginForm,UpdateAccountForm,PostForm,RequestResetForm,ResetPasswordForm,CommentForm,UserChartDayForm
from flaskblog.models import User,Post,Role,Comment
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message
import secrets
import os
from PIL import Image
from flask_restful import inputs
from datetime import datetime,timedelta
# dummyData=[
#     {
#         'author':'Corey Shafer',
#         'title':'Blog post 1',
#         'content':'First post ocntent',
#         'date_posted':'April 20, 2018'
#     },
#     {
#         'author': 'Jane done',
#         'title': 'Blog post 2',
#         'content': 'Seoncd post ocntent',
#         'date_posted': 'April 22, 2018'
#     },
# ]


@app.route('/')
@app.route('/home')
def home():
    #posts=Post.query.all()
    #http://127.0.0.1:5000/home?page_id=1
    #this page_id must be consistant with line 29 and 31 in home.html url_for
    page=request.args.get('page_id',1,type=int)
    posts=Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    #form=PageForm()
    return render_template('home.html',title='home',posts=posts)
@app.route('/about')
def about():
    return render_template('about.html',title='Abouutt')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()

    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('login'))


    return render_template('register.html',title='Register',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)

            #if user tries to access /account before login, we will do it after login
            next_page=request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))

        else:
            flash('Wrong username or password','danger')

    return render_template('login.html',title='Log In',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static','profile_pics',picture_fn)

    output_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account',methods=['GET','POST'])
@login_required
def account():
    form=UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_fn=save_picture(form.picture.data)
            #print(form.picture.data)

            #better delete old profile pic of this user
            if current_user.image_file!='default.jpg':
                old_pic=os.path.join(app.root_path,'static','profile_pics',current_user.image_file)
                os.remove(old_pic)

            current_user.image_file=picture_fn

        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Info Changed','success')
        return redirect(url_for('account'))
    elif request.method=='GET':
        form.username.data=current_user.username
        form.email.data=current_user.email
    image_file=url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html',title='account',image_file=image_file,form=form)

@app.route('/account/delete',methods=['POST'])
@login_required
def delete_account():
    user=User.query.filter_by(id=current_user.id).first()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted!','success')
    return redirect(url_for('home'))


@app.route('/admin')
@login_required
def admin():
    if not current_user.role.is_admin:
        flash('You don\'t have privilege to view this page','warning')
        return redirect(url_for('home'))
    area_chart={'title':'New User Joined In past 30 days',
                'legend':'User joined on this day',
                'labels':[],
                'values':[]}
    earliest_date_registered=User.query.order_by(User.date_registered).first().date_registered
    curr_day=datetime.utcnow()
    days_difference=(curr_day-earliest_date_registered).days
    for i in range(min(30,days_difference+2),0,-1):
        d1=curr_day-timedelta(days=i)
        d2=curr_day-timedelta(days=i-1)
        number_of_user_joined_between_d1_d2=len(User.query.filter(User.date_registered>=d1).filter(User.date_registered<d2).all())
        area_chart['labels'].append(d1.strftime('%Y/%m/%d'))
        area_chart['values'].append(number_of_user_joined_between_d1_d2)

    pie_chart={'title':'User Composition',
               'labels':[role.role for role in Role.query.all()],
               'values':[len(User.query.filter(User.role_id==role.id).all()) for role in Role.query.all()]}

    return render_template('/admin/dashboard.html',title='Admin',area_chart=area_chart,pie_chart=pie_chart,page_header='Dashboard')

@app.route('/admin/user_table')
@login_required
def user_table():
    if not current_user.role.is_admin:
        flash('You don\'t have privilege to view this page','warning')
        return redirect(url_for('home'))
    role = request.args.get('role', 'normal_user', type=str)
    show_post=request.args.get('post',False,type=inputs.boolean)
    posts=None
    if show_post:
        #posts=db.engine.execute('select post.id,post.title,post.date_posted,"user".username from post, role,"user" where role.role={} and "user".role_id=role.id'.format(f'\'{role}\''))
        posts = Post.query.join(User, Post.user_id == User.id).join(Role, User.role_id == Role.id).filter(Role.role == role).all()
    #still cannot avoid writing sql queries
    #users=db.engine.execute('select * from role,"user" where role.role={} and "user".role_id=role.id'.format(f'\'{role}\''))
    users = User.query.join(Role, User.role_id == Role.id).filter(Role.role == role).all()
    return render_template('/admin/user_table.html',title='Table',users=users,posts=posts,show_post=show_post)

@app.route('/user/<int:user_id>/assign',methods=['POST'])
@login_required
def assign_admin(user_id):
    user=User.query.get_or_404(user_id)
    if user:
        user.role_id=2
        db.session.commit()
        flash(f'{user.username} Promoted!', 'success')
    else:
        abort(403)
    return redirect(url_for('admin'))

@app.route('/user/<int:user_id>/remove',methods=['POST'])
@login_required
def remove_admin(user_id):
    user=User.query.get_or_404(user_id)
    if user:
        user.role_id=1
        db.session.commit()
        flash(f'{user.username} Demoted!', 'success')
    else:
        abort(403)
    return redirect(url_for('admin'))

@app.route('/admin/user_chart',methods=['GET','POST'])
@login_required
def user_chart():
    if not current_user.role.is_admin:
        flash('You don\'t have privilege to view this page','warning')
        return redirect(url_for('home'))
    form=UserChartDayForm()
    if form.validate_on_submit():
        past_day=form.day.data
    else:
        past_day=30
    earliest_date_registered = User.query.order_by(User.date_registered).first().date_registered
    curr_day = datetime.utcnow()
    days_difference = (curr_day - earliest_date_registered).days
    labels=[]
    values=[]
    ymax=0
    for i in range(min(past_day, days_difference + 2), 0, -1):
        d1 = curr_day - timedelta(days=i)
        d2=curr_day-timedelta(days=i-1)
        post_count=len(Post.query.filter(Post.date_posted>=d1).filter(Post.date_posted<d2).all())
        comment_count=len(Comment.query.filter(Comment.date_commented>=d1).filter(Comment.date_commented<d2).all())
        new_user_count=len(User.query.filter(User.date_registered>=d1).filter(User.date_registered<d2).all())
        active_pts=new_user_count*10+post_count*5+comment_count
        labels.append(d1.strftime('%Y/%m/%d'))
        values.append(active_pts)
        ymax=max(ymax,active_pts)
    ymax*=1.5
    return render_template('/admin/user_chart.html',page_header='Charts',labels=labels,values=values,form=form,ymax=ymax,day=past_day)

@app.route('/admin/post_chart',methods=['GET','POST'])
@login_required
def post_chart():
    if not current_user.role.is_admin:
        flash('You don\'t have privilege to view this page','warning')
        return redirect(url_for('home'))
    form=UserChartDayForm()
    if form.validate_on_submit():
        past_day=form.day.data
    else:
        past_day=30
    earliest_date_registered = User.query.order_by(User.date_registered).first().date_registered
    curr_day = datetime.utcnow()
    days_difference = (curr_day - earliest_date_registered).days
    labels=[]
    values=[]
    ymax=0
    for i in range(min(past_day, days_difference + 2), 0, -1):
        d1 = curr_day - timedelta(days=i)
        d2=curr_day-timedelta(days=i-1)
        post_count=len(Post.query.filter(Post.date_posted>=d1).filter(Post.date_posted<d2).all())
        labels.append(d1.strftime('%Y/%m/%d'))
        values.append(post_count)
        ymax=max(ymax,post_count)
    ymax*=1.5
    return render_template('/admin/post_chart.html',page_header='Charts',labels=labels,values=values,form=form,ymax=ymax,day=past_day)

@app.route('/post/new',methods=['GET','POST'])
@login_required
def new_post():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()

        flash('Your post ahs benn created','success')
        return redirect(url_for('post',post_id=post.id))

    return render_template('create_post.html',title='New Post',form=form,legend='New Post')

@app.route('/post/<int:post_id>',methods=['GET','POST'])
def post(post_id):
    post=Post.query.get_or_404(post_id)
    # form=CommentForm()
    # if form.validate_on_submit():
    #     comment=Comment(replyto=form.replyto.data,content=form.content.data,post=post)
    #     db.sesseion.add(comment)
    #     db.session.commit()
    #
    # elif request.method=='GET':
    #     form.replyto.data=post.author.username

    return render_template('post.html',title=post.title,post=post)

@app.route('/post/<int:post_id>/reply_to/<string:username>',methods=['GET','POST'])
@login_required
def comment(post_id,username):
    post = Post.query.get_or_404(post_id)
    #print(post)
    form=CommentForm()
    if form.validate_on_submit():
        comment = Comment(replyto=username,content=form.content.data, post=post,author=current_user)
        #print(comment.replyto)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('post',post_id=post.id))
    return render_template('comment.html',title='comment',form=form,replyto=username)



@app.route('/post/<int:post_id>/update',methods=['GET','POST'])
@login_required
def update_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author !=current_user:
        abort(403)
    form=PostForm()


    if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash('Post updated!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method=='GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html',title='Update Post',form=form,legend='Update Post')

@app.route('/post/<int:post_id>/delete',methods=['POST'])
@login_required
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if current_user.role.delete_post or current_user==post.author:
        db.session.delete(post)
        db.session.commit()
        flash('Post Deleted!', 'success')
        if current_user.role.delete_post:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('home'))
    else:
        abort(403)
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_posts(username):
    user=User.query.filter_by(username=username).first_or_404()
    page=request.args.get('page',1,type=int)
    posts=Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('user_posts.html',posts=posts,user=user)


def send_rest_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Request',sender='nonreply@demp.cpm',recipients=[user.email])
    msg.body='Te reset Passowrd, use following link: \n' \
             'localhost:5000/{}\n' \
             'If you did not make this request, just ignore it'.format(url_for('reset_token',token=token,_extrenal=True))
    mail.send(msg)


@app.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        send_rest_email(user)
        flash('An password reset email has been sent to '+form.email.data,'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title='Reset Password',form=form)

@app.route('/reset_password/<string:token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=User.verify_reset_token(token)
    if not user:
        flash('That token is expired','warning')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash(f'password updated {user.username}!','success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',title='Reset Password',form=form)

# @app.route('/resume')
# def resume():
#     return render_template('resume.html',title='Resume')


