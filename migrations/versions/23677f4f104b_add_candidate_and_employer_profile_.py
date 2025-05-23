"""Add candidate and employer profile relationships to User

Revision ID: 23677f4f104b
Revises: a3b5502b27b0
Create Date: 2025-05-16 01:42:07.124968

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23677f4f104b'
down_revision = 'a3b5502b27b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_active')
        batch_op.drop_column('created_at')
        batch_op.drop_column('updated_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.BOOLEAN(), nullable=True))

    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), nullable=False),
    sa.Column('password_hash', sa.VARCHAR(length=128), nullable=False),
    sa.Column('role', sa.VARCHAR(length=20), nullable=False),
    sa.Column('fullname', sa.VARCHAR(length=150), nullable=True),
    sa.Column('field', sa.VARCHAR(length=100), nullable=True),
    sa.Column('experience', sa.TEXT(), nullable=True),
    sa.Column('skills', sa.VARCHAR(length=255), nullable=True),
    sa.Column('video', sa.VARCHAR(length=255), nullable=True),
    sa.Column('company_name', sa.VARCHAR(length=150), nullable=True),
    sa.Column('industry', sa.VARCHAR(length=100), nullable=True),
    sa.Column('contact_person', sa.VARCHAR(length=150), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###
