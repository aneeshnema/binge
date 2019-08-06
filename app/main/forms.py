from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, TextAreaField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Length, NumberRange
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(original_username,*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Username already taken, please use a different username')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class ReviewForm(FlaskForm):
    rating = DecimalField('Rating', validators=[DataRequired(), NumberRange(min=0.5, max=5.0)], places=1)
    body = TextAreaField('Review', validators=[Length(max=256)])
    submit = SubmitField('Submit')