"""empty message

Revision ID: 72ab8ab3c739
Revises: 69820d5ffd1f
Create Date: 2017-03-18 19:03:28.763997

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '72ab8ab3c739'
down_revision = '69820d5ffd1f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dwg_record', sa.Column('date', sa.Date(), nullable=False))
    op.drop_column('dwg_record', 'datetime')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dwg_record', sa.Column('datetime', mysql.DATETIME(), nullable=False))
    op.drop_column('dwg_record', 'date')
    # ### end Alembic commands ###
