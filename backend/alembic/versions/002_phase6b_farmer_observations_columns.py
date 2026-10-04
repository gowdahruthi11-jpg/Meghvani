"""Phase 6B: Add observation metadata and validation columns to farmer_observations

Revision ID: 002_phase6b
Revises: 001_phase6a
Create Date: 2026-10-02
"""
from alembic import op
import sqlalchemy as sa

revision = '002_phase6b'
down_revision = '001_phase6a'
branch_labels = None
depends_on = None

def upgrade():
    try:
        with op.batch_alter_table('farmer_observations') as batch_op:
            batch_op.add_column(sa.Column('village_id', sa.Integer(), nullable=True))
            batch_op.add_column(sa.Column('observation_time', sa.String(length=20), nullable=True))
            batch_op.add_column(sa.Column('crop_id', sa.String(length=50), nullable=True))
            batch_op.add_column(sa.Column('notes', sa.String(length=500), nullable=True))
            batch_op.add_column(sa.Column('validation_status', sa.String(length=50), nullable=True, server_default='PENDING_REVIEW'))
            batch_op.add_column(sa.Column('reference_rainfall_mm', sa.Float(), nullable=True))
            batch_op.add_column(sa.Column('comparison_notes', sa.String(length=500), nullable=True))
    except Exception:
        pass

def downgrade():
    with op.batch_alter_table('farmer_observations') as batch_op:
        batch_op.drop_column('comparison_notes')
        batch_op.drop_column('reference_rainfall_mm')
        batch_op.drop_column('validation_status')
        batch_op.drop_column('notes')
        batch_op.drop_column('crop_id')
        batch_op.drop_column('observation_time')
        batch_op.drop_column('village_id')
