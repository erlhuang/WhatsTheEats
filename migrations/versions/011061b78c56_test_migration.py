"""test migration

Revision ID: 011061b78c56
Revises: 056bd037fb8d
Create Date: 2019-09-10 13:42:54.789898

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011061b78c56'
down_revision = '056bd037fb8d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('listing', sa.Column('atest', sa.String(length=50), nullable=True))
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_foreign_key(None, 'item', 'listing', ['listing_id'], ['id'])
    # op.add_column('listing', sa.Column('acronym', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    op.drop_column('listing', 'atest')
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_column('listing', 'acronym')
    # op.drop_constraint(None, 'item', type_='foreignkey')
    # ### end Alembic commands ###