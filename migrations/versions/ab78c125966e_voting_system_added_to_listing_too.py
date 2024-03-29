"""voting system added to listing too

Revision ID: ab78c125966e
Revises: d583f5dad208
Create Date: 2019-09-13 00:12:19.759497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab78c125966e'
down_revision = 'd583f5dad208'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('listing', sa.Column('downvotes', sa.Integer(), nullable=True))
    op.add_column('listing', sa.Column('upvotes', sa.Integer(), nullable=True))
    op.add_column('listing', sa.Column('votedown', sa.Boolean(), nullable=True))
    op.add_column('listing', sa.Column('voteup', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('listing', 'voteup')
    op.drop_column('listing', 'votedown')
    op.drop_column('listing', 'upvotes')
    op.drop_column('listing', 'downvotes')
    # ### end Alembic commands ###
