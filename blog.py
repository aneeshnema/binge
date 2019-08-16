from app import create_app, db, search
from app.models import User, Post, Movie, Review

app = create_app()
app.app_context().push()
from app.recommender import Recommender
Recommender.restart()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'search': search, 'User': User, 'Post': Post, 'Movie': Movie, 'Review': Review, 'Recommender': Recommender}