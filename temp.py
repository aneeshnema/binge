from app import app, db
from app.models import User, Post, Movie, Review
from datetime import datetime

users = User.query.all()
for u in users:
    u.last_recommended = datetime(1970,1,1,0,0,0)

movies = Movie.query.all()
for m in movies:
    m.last_recommended = datetime(1970,1,1,0,0,0)

db.session.commit()