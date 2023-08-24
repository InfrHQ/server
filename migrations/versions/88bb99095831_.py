"""empty message

Revision ID: 88bb99095831
Revises: c8bd3f20223c
Create Date: 2023-08-24 17:43:52.739733

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '88bb99095831'
down_revision = 'c8bd3f20223c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('apikey', schema=None) as batch_op:
        batch_op.alter_column('status',
                              existing_type=postgresql.ENUM('active', 'inactive', name='status_enum'),
                              type_=sa.String(),
                              nullable=False)
        batch_op.create_unique_constraint(None, ['id'])

    with op.batch_alter_table('device', schema=None) as batch_op:
        batch_op.alter_column('status',
                              existing_type=postgresql.ENUM('active', 'inactive', name='status_enum'),
                              type_=sa.String(),
                              nullable=False)
        batch_op.alter_column('device_type',
                              existing_type=postgresql.ENUM('desktop', 'mobile', 'tablet', name='device_type_enum'),
                              type_=sa.String(),
                              nullable=False)
        batch_op.create_unique_constraint(None, ['id'])

    with op.batch_alter_table('segment', schema=None) as batch_op:
        batch_op.alter_column('status',
                              existing_type=postgresql.ENUM('active', 'inactive', name='status_enum'),
                              type_=sa.String(),
                              nullable=False)
        batch_op.alter_column('item_type',
                              existing_type=postgresql.ENUM('screenshot', name='item_type_enum'),
                              type_=sa.String(),
                              nullable=False)
        batch_op.create_unique_constraint(None, ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('status',
                              existing_type=postgresql.ENUM('active', 'inactive', name='status_enum'),
                              type_=sa.String(),
                              nullable=False)
        batch_op.create_unique_constraint(None, ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('status',
                              existing_type=sa.String(),
                              type_=postgresql.ENUM('active', 'inactive', name='status_enum'),
                              nullable=True)

    with op.batch_alter_table('segment', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('item_type',
                              existing_type=sa.String(),
                              type_=postgresql.ENUM('screenshot', name='item_type_enum'),
                              nullable=True)
        batch_op.alter_column('status',
                              existing_type=sa.String(),
                              type_=postgresql.ENUM('active', 'inactive', name='status_enum'),
                              nullable=True)

    with op.batch_alter_table('device', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('device_type',
                              existing_type=sa.String(),
                              type_=postgresql.ENUM('desktop', 'mobile', 'tablet', name='device_type_enum'),
                              nullable=True)
        batch_op.alter_column('status',
                              existing_type=sa.String(),
                              type_=postgresql.ENUM('active', 'inactive', name='status_enum'),
                              nullable=True)

    with op.batch_alter_table('apikey', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('status',
                              existing_type=sa.String(),
                              type_=postgresql.ENUM('active', 'inactive', name='status_enum'),
                              nullable=True)

    # ### end Alembic commands ###
