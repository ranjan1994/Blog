from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField,TextAreaField
from wtforms.validators import InputRequired, Email, Length


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