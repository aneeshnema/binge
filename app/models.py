from flask import current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask_sqlalchemy import SQLAlchemy

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

recommend = db.Table('recommend',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), index=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')))

similarto = db.Table('similarto',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), index=True),
    db.Column('similar_id', db.Integer, db.ForeignKey('movie.id')))

class User(UserMixin, db.Model):
    __searchable__ = ['username']
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    reviews = db.relationship('Review', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    recommended = db.relationship('Movie', secondary=recommend,
        lazy='dynamic')
    last_recommended = db.Column(db.DateTime, default=datetime(1970,1,1,0,0,0))
    role = db.Column(db.String(5), default='USER')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def set_role(self, role):
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def followed_posts(self):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter(Post.user_id == self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    
    def followed_reviews(self):
        followed = Review.query.join(followers, (followers.c.followed_id == Review.user_id)).filter(followers.c.follower_id == self.id)
        own = Review.query.filter(Review.user_id == self.id)
        return followed.union(own).order_by(Review.timestamp.desc())
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time()+ expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

#@whooshee.register_model('title')
class Movie(db.Model):
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=True, nullable=False)
    released = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    runtime = db.Column(db.Integer)
    genre = db.Column(db.String(100))
    director = db.Column(db.String(64))
    actors = db.Column(db.String(160))
    plot = db.Column(db.String(600))
    poster = db.Column(db.String(300))
    imdb_rating = db.Column(db.Float(4))
    imdb_id = db.Column(db.String(9))
    production = db.Column(db.String(64))
    rating = db.Column(db.Float(4), default=0)
    count = db.Column(db.Integer, default=0)
    reviews = db.relationship('Review', backref='movie', lazy='dynamic')
    similar = db.relationship('Movie', secondary=similarto,
        primaryjoin=(similarto.c.movie_id == id),
        secondaryjoin=(similarto.c.similar_id == id),
        lazy='dynamic')
    last_recommended = db.Column(db.DateTime, default=datetime(1970,1,1,0,0,0))

    def __repr__(self):
        return '<Movie {} {:.2f}>'.format(self.title, self.rating)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    rating = db.Column(db.Float(4))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.String(256))

    def __repr__(self):
        return '<Review {} {}>'.format(self.movie_id, self.rating)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))