"""Fix password column to LargeBinary

Revision ID: 172ba5f58fbb
Revises: 71cc11398f2a
Create Date: 2025-03-03 08:10:00.716143

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '172ba5f58fbb'
down_revision = '71cc11398f2a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password', 
                              existing_type=sa.String(120), 
                              type_=sa.LargeBinary, 
                              nullable=False, 
                              postgresql_using='password::bytea')
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.alter_column('password', 
                              existing_type=sa.String(120), 
                              type_=sa.LargeBinary, 
                              nullable=False, 
                              postgresql_using='password::bytea')
    with op.batch_alter_table('instructor', schema=None) as batch_op:
        batch_op.alter_column('password', 
                              existing_type=sa.String(120), 
                              type_=sa.LargeBinary, 
                              nullable=False, 
                              postgresql_using='password::bytea')

def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password', 
                              existing_type=sa.LargeBinary, 
                              type_=sa.String(120), 
                              nullable=False, 
                              postgresql_using='password::text')
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.alter_column('password', 
                              existing_type=sa.LargeBinary, 
                              type_=sa.String(120), 
                              nullable=False, 
                              postgresql_using='password::text')
    with op.batch_alter_table('instructor', schema=None) as batch_op:
        batch_op.alter_column('password', 
                              existing_type=sa.LargeBinary, 
                              type_=sa.String(120), 
                              nullable=False, 
                              postgresql_using='password::text')
    # ### end Alembic commands ###
