"""add users and groups

Revision ID: b482ffe6da23
Revises: 
Create Date: 2019-01-06 20:06:16.863528

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b482ffe6da23'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('groupName', sa.String(length=140), nullable=True),
    sa.Column('groupDescription', sa.String(length=140), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_artist_email'), 'artist', ['email'], unique=True)
    op.create_index(op.f('ix_artist_username'), 'artist', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_artist_username'), table_name='artist')
    op.drop_index(op.f('ix_artist_email'), table_name='artist')
    op.drop_table('artist')
    op.drop_table('group')
    # ### end Alembic commands ###
