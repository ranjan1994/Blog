from flask import Flask, render_template, redirect, url_for,request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
import datetime 
from wtforms import StringField, PasswordField, BooleanField,TextAreaField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_permissions.core import Permissions
from flask_permissions.decorators import user_is, user_has

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:rakesh123@localhost/blog"
app.config['SECRET_KEY']='super-secret'
app.config['SECURITY_REGISTERABLE']=True
app.debug = True
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
perms = Permissions(app, db, current_user)

#models class, will put it at seperate location and import here
class User(UserMixin, db.Model):
    """ User field for creating new account """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    roles=db.Column(db.String())

class Content(UserMixin, db.Model):
    """ Creating field for new blog post """

    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String())
    detail=db.Column(db.String())
    username=db.Column(db.String())
    time=db.Column(db.DateTime())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Form class, will put it seperate location and import here
class LoginForm(FlaskForm):
    """ Form field for login-in registered """
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    """ Form field for registering the user """
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

class ContentForm(FlaskForm):
    """ New blog post Form """
    title=TextAreaField('title',validators=[InputRequired(),Length(min=10, max=150)])
    detail=TextAreaField('detail',validators=[InputRequired(),Length(min=50, max=1000)])

@app.route('/')
@login_required
def index():
    """ Dashboard page for the blog, contain all the post created """

    data=Content.query.order_by(Content.id)
    return render_template('index.html',name=current_user.username,data=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Login page for registered user """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """ Signup page for new user """

    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        
        if User.query.filter_by(email=form.email.data).first():
            return "<h1>Email Id already exist</h1>"
        else:
        #assigning basic role for every login
        #Creating role of admin from PgAdmin    
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,roles='None')
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/<slug>/',methods=['GET', 'POST'])
@login_required
def detail(slug):
    """ Detail for the clicked post on the index page """

    content = Content.query.filter_by(id=slug).first()
    return render_template('post.html', content=content)

@app.route('/create',methods=['GET', 'POST'])
@login_required
def create():
    """ Creating new post """

    form=ContentForm()

    if form.validate_on_submit():
        new_content = Content(title=form.title.data, detail=form.detail.data,username=current_user.username,time=datetime.datetime.now())
        db.session.add(new_content)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('create.html', form=form)            

@app.route('/<slug>/edit',methods=['GET', 'POST'])
@login_required
def edit(slug):
    """ Editing the clicked post from the index page """

    data = Content.query.filter_by(id=slug).first()
    form=ContentForm()
    #I found best way to re-populate is to partion request btw GET and POST
    if request.method == 'GET':
        form.title.data= data.title
        form.detail.data= data.detail
        return render_template('edit.html', form=form,data=data)

    elif request.method == 'POST':    
        if form.validate_on_submit():
            data.title=form.title.data
            data.detail=form.detail.data
            db.session.commit()
            return redirect(url_for('index'))


@app.route('/<slug>/delete',methods=['GET', 'POST'])
@login_required
@user_is('admin')
def delete(slug):
    """ Deleting the clicked post from index page """
    #Only admin role user has permission to delete post
    data = Content.query.filter_by(id=slug).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/admin',methods=['GET', 'POST'])
@login_required
@user_is('admin')
def admin_dash():
    """Created an Dashboard with total number of posts made by specific user and other overview """
    data=Content.query.all()
    user = User.query.all()
    rows = Content.query.count()
    return render_template('admin.html', data=data,user=user,rows=rows)       


@app.route('/logout')
@login_required
def logout():
    """ Deleting the login session """

    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()


