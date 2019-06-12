from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
#import wtforms

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(5,12)])
    password = PasswordField('Password', validators=[DataRequired(), Length(5,12)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')