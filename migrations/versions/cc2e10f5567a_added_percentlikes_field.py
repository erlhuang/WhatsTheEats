"""added percentlikes field

Revision ID: cc2e10f5567a
Revises: 8ec6c5839c3d
Create Date: 2019-09-23 17:04:42.648822

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc2e10f5567a'
down_revision = '8ec6c5839c3d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item', sa.Column('percentLikes', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('item', 'percentLikes')
    # ### end Alembic commands ###
