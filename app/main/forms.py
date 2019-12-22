from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, TextAreaField, DecimalField, SelectField
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

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(0.5*x, 0.5*x) for x in range(1,11)], coerce=float)
    body = TextAreaField('Review', validators=[Length(max=1024)])
    submit = SubmitField('Submit')