"""Add inbound_messages table for real SMS webhook auditing and idempotency

Revision ID: 004_inbound_messages
Revises: 003_phase8b
Create Date: 2026-10-04
"""
from alembic import op
import sqlalchemy as sa

revision = '004_inbound_messages'
down_revision = '003_phase8b'
branch_labels = None
depends_on = None

def upgrade():
    try:
        op.create_table(
            'inbound_messages',
            sa.Column('id', sa.String(length=36), primary_key=True),
            sa.Column('provider', sa.String(length=32), nullable=False, server_default='TWILIO'),
            sa.Column('provider_message_id', sa.String(length=128), nullable=True),
            sa.Column('from_phone', sa.String(length=32), nullable=False),
            sa.Column('to_phone', sa.String(length=32), nullable=True),
            sa.Column('message_body', sa.Text(), nullable=False),
            sa.Column('normalized_body', sa.String(length=255), nullable=True),
            sa.Column('received_at', sa.DateTime(), nullable=False),
            sa.Column('processing_status', sa.String(length=32), nullable=False, server_default='RECEIVED'),
            sa.Column('registration_step_before', sa.String(length=32), nullable=True),
            sa.Column('registration_step_after', sa.String(length=32), nullable=True),
            sa.Column('farmer_id', sa.String(length=36), sa.ForeignKey('farmers.id', ondelete='SET NULL'), nullable=True),
            sa.Column('reply_message', sa.Text(), nullable=True),
            sa.Column('reply_status', sa.String(length=32), nullable=True),
            sa.Column('error_message', sa.Text(), nullable=True),
        )
        op.create_index('ix_inbound_messages_provider_message_id', 'inbound_messages', ['provider_message_id'], unique=True)
        op.create_index('ix_inbound_messages_from_phone', 'inbound_messages', ['from_phone'])
        op.create_index('ix_inbound_messages_received_at', 'inbound_messages', ['received_at'])
        op.create_index('ix_inbound_messages_farmer_id', 'inbound_messages', ['farmer_id'])
    except Exception:
        pass

def downgrade():
    try:
        op.drop_table('inbound_messages')
    except Exception:
        pass
