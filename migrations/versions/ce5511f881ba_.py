"""empty message

Revision ID: ce5511f881ba
Revises: cc278c82f016
Create Date: 2021-07-23 22:15:59.243074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ce5511f881ba'
down_revision = 'cc278c82f016'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cars',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('model', sa.String(length=250), nullable=False),
    sa.Column('image', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rentals',
    sa.Column('cars_id', sa.Integer(), nullable=False),
    sa.Column('users_id', sa.Integer(), nullable=False),
    sa.Column('from_date', sa.DateTime(), nullable=False),
    sa.Column('to_date', sa.DateTime(), nullable=False),
    sa.Column('available_from', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['cars_id'], ['cars.id'], ),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rentals')
    op.drop_table('cars')
    # ### end Alembic commands ###
