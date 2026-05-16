"""Initial schema: enums and all tables

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extensión para UUIDs
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # Enums
    level_band_enum = postgresql.ENUM('B1', 'B2', 'C1', name='level_band_enum')
    dialect_segment_enum = postgresql.ENUM('east_coast', 'midwest', name='dialect_segment_enum')
    module_type_enum = postgresql.ENUM('reading', 'listening', 'writing', 'speaking', name='module_type_enum')
    level_band_enum.create(op.get_bind())
    dialect_segment_enum.create(op.get_bind())
    module_type_enum.create(op.get_bind())

    # Tabla users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('level_band', postgresql.ENUM('B1', 'B2', 'C1', name='level_band_enum', create_type=False), nullable=False, server_default='B1'),
        sa.Column('xp_total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # Tabla lessons
    op.create_table(
        'lessons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('dialect_segment', postgresql.ENUM('east_coast', 'midwest', name='dialect_segment_enum', create_type=False), nullable=False),
        sa.Column('level_band', postgresql.ENUM('B1', 'B2', 'C1', name='level_band_enum', create_type=False), nullable=False),
        sa.Column('day_order', sa.Integer(), nullable=False),
        sa.Column('audio_url', sa.String(2048), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_lessons_dialect_level', 'lessons', ['dialect_segment', 'level_band'])
    op.create_index('idx_lessons_day_order', 'lessons', ['day_order'])

    # Tabla lesson_progress
    op.create_table(
        'lesson_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('module_type', postgresql.ENUM('reading', 'listening', 'writing', 'speaking', name='module_type_enum', create_type=False), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('score >= 0 AND score <= 100', name='ck_lesson_progress_score'),
    )
    op.create_index('idx_lesson_progress_user', 'lesson_progress', ['user_id'])
    op.create_index('idx_lesson_progress_lesson', 'lesson_progress', ['lesson_id'])
    op.create_index('idx_lesson_progress_user_module', 'lesson_progress', ['user_id', 'module_type'])

    # Tabla vocabulary_items
    op.create_table(
        'vocabulary_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('term', sa.String(255), nullable=False),
        sa.Column('definition', sa.Text(), nullable=False),
        sa.Column('example_sentence', sa.Text(), nullable=True),
        sa.Column('dialect_segment', postgresql.ENUM('east_coast', 'midwest', name='dialect_segment_enum', create_type=False), nullable=True),
        sa.Column('level_band', postgresql.ENUM('B1', 'B2', 'C1', name='level_band_enum', create_type=False), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_vocab_dialect', 'vocabulary_items', ['dialect_segment'])
    op.create_index('idx_vocab_level', 'vocabulary_items', ['level_band'])

    # Tabla user_vocabulary
    op.create_table(
        'user_vocabulary',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vocabulary_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vocabulary_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mastered', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('correct_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_reviewed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('user_id', 'vocabulary_item_id'),
    )
    op.create_index('idx_user_vocab_mastered', 'user_vocabulary', ['user_id', 'mastered'])

    # Tabla oral_reports
    op.create_table(
        'oral_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('raw_json', postgresql.JSONB(), nullable=False),
        sa.Column('fluency_score', sa.Integer(), nullable=False),
        sa.Column('pronunciation_score', sa.Integer(), nullable=False),
        sa.Column('session_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('submitted_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('fluency_score >= 0 AND fluency_score <= 100', name='ck_oral_fluency_score'),
        sa.CheckConstraint('pronunciation_score >= 0 AND pronunciation_score <= 100', name='ck_oral_pronunciation_score'),
    )
    op.create_index('idx_oral_reports_user', 'oral_reports', ['user_id'])
    op.create_index('idx_oral_reports_submitted', 'oral_reports', ['user_id', 'submitted_at'])
    # Índice GIN para consultas JSONB
    op.create_index('idx_oral_reports_raw_json', 'oral_reports', ['raw_json'], postgresql_using='gin')

    # Tabla streaks
    op.create_table(
        'streaks',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity_date', sa.Date(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('streaks')
    op.drop_index('idx_oral_reports_raw_json', table_name='oral_reports')
    op.drop_index('idx_oral_reports_submitted', table_name='oral_reports')
    op.drop_index('idx_oral_reports_user', table_name='oral_reports')
    op.drop_table('oral_reports')
    op.drop_index('idx_user_vocab_mastered', table_name='user_vocabulary')
    op.drop_table('user_vocabulary')
    op.drop_index('idx_vocab_level', table_name='vocabulary_items')
    op.drop_index('idx_vocab_dialect', table_name='vocabulary_items')
    op.drop_table('vocabulary_items')
    op.drop_index('idx_lesson_progress_user_module', table_name='lesson_progress')
    op.drop_index('idx_lesson_progress_lesson', table_name='lesson_progress')
    op.drop_index('idx_lesson_progress_user', table_name='lesson_progress')
    op.drop_table('lesson_progress')
    op.drop_index('idx_lessons_day_order', table_name='lessons')
    op.drop_index('idx_lessons_dialect_level', table_name='lessons')
    op.drop_table('lessons')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')

    # Drop enums
    postgresql.ENUM(name='module_type_enum').drop(op.get_bind())
    postgresql.ENUM(name='dialect_segment_enum').drop(op.get_bind())
    postgresql.ENUM(name='level_band_enum').drop(op.get_bind())
