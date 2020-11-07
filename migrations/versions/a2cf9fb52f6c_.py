"""empty message

Revision ID: a2cf9fb52f6c
Revises: 
Create Date: 2020-11-07 11:40:42.445107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a2cf9fb52f6c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('presentations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('rooms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('schedule',
    sa.Column('date_start', sa.DateTime(), nullable=False),
    sa.Column('id_presentation', sa.Integer(), nullable=False),
    sa.Column('id_room', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_presentation'], ['presentations.id'], ),
    sa.ForeignKeyConstraint(['id_room'], ['rooms.id'], ),
    sa.PrimaryKeyConstraint('id_presentation', 'id_room')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_table('schedule')
    op.drop_table('rooms')
    op.drop_table('roles')
    op.drop_table('presentations')
    # ### end Alembic commands ###
