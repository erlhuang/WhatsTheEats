"""new fields in listing model

Revision ID: 056bd037fb8d
Revises: 571d749ac1d8
Create Date: 2019-09-09 16:21:42.741146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '056bd037fb8d'
down_revision = '571d749ac1d8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item', sa.Column('listing_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'item', 'listing', ['listing_id'], ['id'])
    op.add_column('listing', sa.Column('acronym', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('listing', 'acronym')
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.drop_column('item', 'listing_id')
    # ### end Alembic commands ###
