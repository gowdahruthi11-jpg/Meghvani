"""Phase 6A Alert Logs Simulation Columns

Revision ID: 001_phase6a
Revises: 
Create Date: 2026-10-02
"""
from alembic import op
import sqlalchemy as sa

revision = '001_phase6a'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    try:
        op.add_column('alert_logs', sa.Column('crop_id', sa.String(length=50), nullable=True))
        op.add_column('alert_logs', sa.Column('decision', sa.String(length=50), nullable=True))
        op.add_column('alert_logs', sa.Column('severity', sa.String(length=50), nullable=True))
        op.add_column('alert_logs', sa.Column('message_type', sa.String(length=50), nullable=True))
        op.add_column('alert_logs', sa.Column('language', sa.String(length=20), server_default='en', nullable=True))
        op.add_column('alert_logs', sa.Column('provider', sa.String(length=50), nullable=True))
        op.add_column('alert_logs', sa.Column('fallback_used', sa.Boolean(), server_default='0', nullable=False))
        op.add_column('alert_logs', sa.Column('fallback_channel', sa.String(length=50), nullable=True))
        op.add_column('alert_logs', sa.Column('reason', sa.Text(), nullable=True))
        op.add_column('alert_logs', sa.Column('external_dispatch', sa.Boolean(), server_default='0', nullable=False))
    except Exception:
        pass

def downgrade():
    pass
