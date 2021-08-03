"""Change PK

Revision ID: 12cc5e329ead
Revises: 10ff0d392845
Create Date: 2021-07-29 14:31:20.500132

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '12cc5e329ead'
down_revision = '10ff0d392845'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('rentals', schema=None) as batch_op:
        batch_op.create_primary_key(constraint_name='cars_id_users_id_from_date',
                                    columns=['cars_id', 'users_id', 'from_date'])


def downgrade():
    with op.batch_alter_table('rentals', schema=None) as batch_op:
        batch_op.drop_constraint('cars_id_users_id_from_date', type_='primary')
