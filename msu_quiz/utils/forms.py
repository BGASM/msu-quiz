from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional
)


class AddQuestionForm(FlaskForm):
    quiz = StringField(
        'Title of Quiz:',
        validators=[DataRequired()]
    )
    course = StringField(
        'Course:',
        validators=[DataRequired()]
    )
    question = TextAreaField(
        'Bulk Enter Questions:',
        validators=[DataRequired()]
    )
    submit = SubmitField('Submit!')


class SignupForm(FlaskForm):
    """User Sign-up Form."""
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    name = StringField(
        'Name or alias',
        validators=[DataRequired()]
    )
    email = StringField(
        'Email',
        validators=[
            Optional(),
            Length(min=6),
            Email(message='Enter a valid email.')]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, message='Select a stronger password.')]
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    """User Log-in Form."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])


class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
