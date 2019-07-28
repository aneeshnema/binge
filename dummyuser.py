from app import app, db
from app.models import User, Post, Movie, Review

if __name__ == '__main__':
    print('adding dummy users to db')
    default_name = 'susan'
    default_pass = 'dog'
    default_email = '@example.com'
    default_about_me = 'susan is cool'
    for i in range(3, 611):
        u = User()
        u.username = default_name+str(i)
        u.email = default_name+str(i)+default_email
        u.about_me = default_about_me
        u.set_password(default_pass)
        db.session.add(u)
    db.session.commit()