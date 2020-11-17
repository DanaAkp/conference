from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    confirm = PasswordField('Repeat password')

    submit = SubmitField('Submit')
