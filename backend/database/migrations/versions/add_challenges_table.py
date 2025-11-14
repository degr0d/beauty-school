"""Add challenges tables

Revision ID: add_challenges
Revises: add_reviews
Create Date: 2025-11-07 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_challenges'
down_revision = 'add_reviews'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем таблицу challenges
    op.create_table(
        'challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('icon_url', sa.Text(), nullable=True),
        sa.Column('points_reward', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('condition_type', sa.String(length=50), nullable=False),
        sa.Column('condition_value', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('end_date', sa.TIMESTAMP(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_challenges_id'), 'challenges', ['id'], unique=False)
    
    # Создаем таблицу user_challenges
    op.create_table(
        'user_challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('joined_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'challenge_id', name='uq_user_challenge')
    )
    op.create_index(op.f('ix_user_challenges_id'), 'user_challenges', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_challenges_id'), table_name='user_challenges')
    op.drop_table('user_challenges')
    op.drop_index(op.f('ix_challenges_id'), table_name='challenges')
    op.drop_table('challenges')


