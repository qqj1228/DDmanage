"""empty message

Revision ID: 7d83926702ee
Revises: 81ca14133623
Create Date: 2017-03-05 16:35:24.164051

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7d83926702ee'
down_revision = '81ca14133623'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role', sa.Column('default', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_role_default'), 'role', ['default'], unique=False)
    op.drop_column('user', 'confirmed')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('confirmed', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_role_default'), table_name='role')
    op.drop_column('role', 'default')
    # ### end Alembic commands ###
