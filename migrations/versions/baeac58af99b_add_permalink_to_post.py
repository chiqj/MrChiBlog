"""add permalink to post

Revision ID: baeac58af99b
Revises: 90cd3fd44a5a
Create Date: 2018-07-27 15:32:37.654566

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'baeac58af99b'
down_revision = '90cd3fd44a5a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('permalink', sa.String(length=128), nullable=False))
    op.create_unique_constraint(None, 'post', ['permalink'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'post', type_='unique')
    op.drop_column('post', 'permalink')
    # ### end Alembic commands ###