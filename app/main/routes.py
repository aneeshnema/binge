from flask import render_template, url_for, flash, redirect, request, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, ReviewForm
from app.models import User, Movie, Review
from app.recommender import Recommender
from app.main import bp
from datetime import datetime

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    Recommender.recommend(current_user)
    carousels = [('Top Recommendations For You', current_user.recommended)]  
    history = [r.movie for r in current_user.reviews.order_by(Review.timestamp.desc()).limit(3)]
    for movie in history:
        Recommender.similar_to(movie)
        carousels.append(('Because You Have Watched {}'.format(movie.title), movie.similar))
    return render_template('index.html', title='Home Page', carousels=carousels)

@bp.route('/feed')
@login_required
def feed():
    page = request.args.get('page', 1, type=int)
    reviews = current_user.followed_reviews().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.feed', page=reviews.next_num) if reviews.has_next else None
    prev_url = url_for('main.feed', page=reviews.prev_num) if reviews.has_prev else None
    return render_template('reviews.html', title='Feed', reviews=reviews.items, heading='Feed', next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    reviews = user.reviews.order_by(Review.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=reviews.next_num) if reviews.has_next else None
    prev_url = url_for('main.user', username=user.username, page=reviews.prev_num) if reviews.has_prev else None
    return render_template('user.html', title=user.username, user=user, reviews=reviews.items, heading='Feed', next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect('main.user', username=username)
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}!'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You unfollowed {}.'.format(username))
    return redirect(url_for('main.user', username=username))

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    reviews = Review.query.order_by(Review.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=reviews.next_num) if reviews.has_next else None
    prev_url = url_for('main.explore', page=reviews.prev_num) if reviews.has_prev else None
    return render_template('reviews.html', title='Explore', reviews=reviews.items, heading='Recent Reviews', next_url=next_url, prev_url=prev_url)

@bp.route('/movie/<movieid>', methods=['GET', 'POST'])
@login_required
def movie(movieid):
    form = ReviewForm()
    movie = Movie.query.get_or_404(movieid)
    review = current_user.reviews.filter(Review.movie_id == movieid).first()
    if form.validate_on_submit():
        if review is None:
            review = Review(rating=form.rating.data, body=form.body.data if form.body.data is not "" else None, author=current_user, movie=movie)
            movie.count += 1
            db.session.add(review)
        else:
            review.rating = form.rating.data
            review.body = form.body.data if form.body.data is not "" else None
            review.timestamp = datetime.utcnow()
        db.session.commit()
        Recommender.need_restart()
        return redirect(url_for('main.movie', movieid=movie.id))
    elif review is not None:
        form.rating.data = review.rating
        form.body.data = review.body
    page = request.args.get('page', 1, type=int)
    reviews = movie.reviews.order_by(Review.body.nullslast(), Review.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.movie', movieid=movie.id, page=reviews.next_num) if reviews.has_next else None
    prev_url = url_for('main.movie', movieid=movie.id, page=reviews.prev_num) if reviews.has_prev else None
    Recommender.similar_to(movie)
    carousels = [('Similar Movies', movie.similar)]    
    return render_template('movie.html', title=movie.title, movie=movie, carousels=carousels, reviews=reviews.items, form=form, next_url=next_url, prev_url=prev_url)

@bp.route('/search')
@login_required
def search():
    keyword = request.args.get('keyword', type=str)
    if (keyword is None) or keyword == '':
        return redirect(url_for('main.index'))
    t = request.args.get('t', 'movie', type=str)
    page = request.args.get('page', 1, type=int)
    mov = True
    if t == 'movie':
        res = Movie.query.msearch(keyword).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    else:
        res = User.query.msearch(keyword).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
        mov = False
    next_url = url_for('main.search', keyword=keyword, t=t, page=res.next_num) if res.has_next else None
    prev_url = url_for('main.search', keyword=keyword, t=t, page=res.prev_num) if res.has_prev else None
    return render_template('search.html', title='Search', keyword=keyword, res=res.items, next_url=next_url, prev_url=prev_url, ismov=mov)