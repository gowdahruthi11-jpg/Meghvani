"""Phase 8B: Add model and advisory provenance columns to alert_logs

Revision ID: 003_phase8b
Revises: 002_phase6b
Create Date: 2026-10-03
"""
from alembic import op
import sqlalchemy as sa

revision = '003_phase8b'
down_revision = '002_phase6b'
branch_labels = None
depends_on = None

def upgrade():
    try:
        with op.batch_alter_table('alert_logs') as batch_op:
            batch_op.add_column(sa.Column('model_version', sa.String(length=50), nullable=True))
            batch_op.add_column(sa.Column('rule_id', sa.String(length=100), nullable=True))
            batch_op.add_column(sa.Column('rule_version', sa.String(length=50), nullable=True))
            batch_op.add_column(sa.Column('threshold_config_hash', sa.String(length=64), nullable=True))
    except Exception:
        pass

def downgrade():
    with op.batch_alter_table('alert_logs') as batch_op:
        batch_op.drop_column('threshold_config_hash')
        batch_op.drop_column('rule_version')
        batch_op.drop_column('rule_id')
        batch_op.drop_column('model_version')
