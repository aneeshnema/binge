import pandas as pd
import numpy as np
from scipy import sparse
from scipy.sparse import csr_matrix
from datetime import datetime, timedelta
from implicit.approximate_als import NMSLibAlternatingLeastSquares
from app.models import Movie, User, Review
from app import db
from sys import stderr

def generate_mat():
    q = Review.query.with_entities(Review.user_id, Review.movie_id, Review.rating)
    df_ratings = pd.read_sql(q.statement, q.session.bind)
    df_pivot = pd.pivot_table(df_ratings, values='rating', index='movie_id', columns='user_id', fill_value=0)
    return csr_matrix(df_pivot.values)

class Recommender:
    mat = None
    tmat = None
    model = None
    update_threshold = 50
    count = None
    last_restart = None
    
    def restart():
        print("RESTART RECOMMENDATION ENGINE", file=stderr)
        Recommender.mat = generate_mat()
        Recommender.tmat = Recommender.mat.transpose()
        Recommender.model = NMSLibAlternatingLeastSquares()
        Recommender.model.fit(Recommender.mat)
        Recommender.last_restart = datetime.utcnow()
        Recommender.count = Review.query.count()
    
    def need_restart():
        if Review.query.count() - Recommender.count > Recommender.update_threshold:
            Recommender.restart()

    def similar_to(movie):
        if movie.last_recommended < Recommender.last_restart:
            print("GENERATING RECOMMENDATION FOR M{}".format(movie.id), file=stderr)
            movie.similar = []
            similar = [mv[0]+1 for mv in Recommender.model.similar_items(movie.id-1, 13)]
            if movie.id in similar:
                similar.remove(movie.id)
            if len(similar) > 12:
                similar = similar[0:12]
            for mv in similar:
                movie.similar.append(Movie.query.get(int(mv)))
            movie.last_recommended = datetime.utcnow()
            db.session.commit()
        else:
            print("USING PRECOMPUTED RECOMMENDATION FOR M{}".format(movie.id), file=stderr)
    
    def recommend(user):
        if user.last_recommended < Recommender.last_restart:
            print("GENERATING RECOMMENDATION FOR U{}".format(user.id), file=stderr)
            user.recommended = []
            recommended = [mv[0]+1 for mv in Recommender.model.recommend(user.id-1, Recommender.tmat, 12)] #filter_already_liked_items=True
            for mv in recommended:
                user.recommended.append(Movie.query.get(int(mv)))
            user.last_recommended = datetime.utcnow()
            db.session.commit()
        else:
            print("USING PRECOMPUTED RECOMMENDATION FOR U{}".format(user.id), file=stderr)
