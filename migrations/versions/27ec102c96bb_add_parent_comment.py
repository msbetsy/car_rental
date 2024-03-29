"""add parent_comment

Revision ID: 27ec102c96bb
Revises: 5628932aad0d
Create Date: 2021-08-10 11:57:48.508188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27ec102c96bb'
down_revision = '5628932aad0d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_comment', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_column('parent_comment')

    # ### end Alembic commands ###
