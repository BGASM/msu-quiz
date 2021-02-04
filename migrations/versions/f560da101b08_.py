"""empty message

Revision ID: f560da101b08
Revises: 9533c3593a91
Create Date: 2021-02-04 07:03:45.223589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f560da101b08'
down_revision = '9533c3593a91'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('exam_question', sa.Column('ans_correct', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('exam_question', 'ans_correct')
    # ### end Alembic commands ###