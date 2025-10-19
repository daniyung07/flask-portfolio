# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, URLField
from wtforms.validators import DataRequired, Email, Length

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email_address = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)]) # Needs min length!

    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email_address = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])

    submit = SubmitField('Login')

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(max=100)])
    description = StringField('Description', validators=[DataRequired(), Length(max=100)])
    link = URLField('Project Link', validators=[DataRequired(), Length(max=100)])