"""movie and reviews

Revision ID: f79cea664d20
Revises: e7a6f221ba69
Create Date: 2019-07-24 20:44:15.951568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f79cea664d20'
down_revision = 'e7a6f221ba69'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('movie',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('released', sa.DateTime(), nullable=True),
    sa.Column('runtime', sa.Integer(), nullable=True),
    sa.Column('genre', sa.String(length=100), nullable=True),
    sa.Column('director', sa.String(length=64), nullable=True),
    sa.Column('actors', sa.String(length=160), nullable=True),
    sa.Column('plot', sa.String(length=600), nullable=True),
    sa.Column('poster', sa.String(length=300), nullable=True),
    sa.Column('imdb_rating', sa.Float(precision=4), nullable=True),
    sa.Column('imdb_id', sa.String(length=9), nullable=True),
    sa.Column('production', sa.String(length=64), nullable=True),
    sa.Column('rating', sa.Float(precision=4), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_movie_imdb_rating'), 'movie', ['imdb_rating'], unique=False)
    op.create_index(op.f('ix_movie_poster'), 'movie', ['poster'], unique=False)
    op.create_index(op.f('ix_movie_rating'), 'movie', ['rating'], unique=False)
    op.create_index(op.f('ix_movie_released'), 'movie', ['released'], unique=False)
    op.create_index(op.f('ix_movie_title'), 'movie', ['title'], unique=False)
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('movie_id', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Float(precision=4), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['movie_id'], ['movie.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_review_timestamp'), 'review', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_review_timestamp'), table_name='review')
    op.drop_table('review')
    op.drop_index(op.f('ix_movie_title'), table_name='movie')
    op.drop_index(op.f('ix_movie_released'), table_name='movie')
    op.drop_index(op.f('ix_movie_rating'), table_name='movie')
    op.drop_index(op.f('ix_movie_poster'), table_name='movie')
    op.drop_index(op.f('ix_movie_imdb_rating'), table_name='movie')
    op.drop_table('movie')
    # ### end Alembic commands ###
