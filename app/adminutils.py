from app import db, admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_login import current_user, login_required
from flask import render_template, url_for, redirect, request
from app.models import User, Movie, Review

class AdminModelView(ModelView):
    @login_required
    def is_accessible(self):
        return current_user.role == 'ADMIN'

    def inaccessible_callback(self, name, **kwargs):
        return render_template('errors/404.html'), 404

class UserModelView(AdminModelView):
    can_create = False
    form_columns = ['username', 'email', 'about_me']
    column_searchable_list = ['username', 'email']
    column_exclude_list = ['password_hash', 'about_me']

class MovieModelView(AdminModelView):
    form_excluded_columns = ['reviews', 'similar', 'last_recommended', 'rating', 'count']
    column_searchable_list = ['title', 'released', 'genre', 'actors', 'director']
    column_exclude_list = ['plot', 'poster', 'last_recommended']

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        if current_user.role != 'ADMIN':
            return render_template('errors/404.html'), 404
        return super(MyAdminIndexView,self).index()

admin.add_view(UserModelView(User, db.session))
admin.add_view(MovieModelView(Movie, db.session))
admin.add_view(AdminModelView(Review, db.session))