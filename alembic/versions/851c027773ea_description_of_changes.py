"""description of changes

Revision ID: 851c027773ea
Revises: 
Create Date: 2024-12-15 16:13:46.986321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '851c027773ea'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('key', sa.String(length=256), nullable=False),
    sa.Column('source', sa.String(length=56), nullable=False),
    sa.Column('extension', sa.String(length=16), nullable=False),
    sa.Column('bucket_path', sa.String(length=512), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_item_images_item_id'), 'item_images', ['item_id'], unique=False)
    op.create_index(op.f('ix_item_images_key'), 'item_images', ['key'], unique=True)
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=50), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('price_negotiable', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('status', sa.Enum('active', 'sold', 'hidden', 'deleted', name='itemstatus'), server_default=sa.text("'active'"), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('description', sa.String(length=1024), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_category_id'), 'items', ['category_id'], unique=False)
    op.create_index(op.f('ix_items_key'), 'items', ['key'], unique=True)
    op.create_index(op.f('ix_items_user_id'), 'items', ['user_id'], unique=False)
    op.create_table('user_verifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(length=10), nullable=False),
    sa.Column('verification_code', sa.String(length=6), nullable=False),
    sa.Column('verification_token', sa.String(length=50), nullable=False, comment='session identifier'),
    sa.Column('verified_at', sa.DateTime(), nullable=True),
    sa.Column('attempts', sa.Integer(), server_default=sa.text('5'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP + INTERVAL '5 minutes'"), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_verifications_phone_number'), 'user_verifications', ['phone_number'], unique=False)
    op.create_index(op.f('ix_user_verifications_user_id'), 'user_verifications', ['user_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('phone_number', sa.String(length=10), nullable=False),
    sa.Column('status', sa.Enum('verified', 'unverified', 'suspended', name='userstatus'), server_default=sa.text("'unverified'"), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_user_verifications_user_id'), table_name='user_verifications')
    op.drop_index(op.f('ix_user_verifications_phone_number'), table_name='user_verifications')
    op.drop_table('user_verifications')
    op.drop_index(op.f('ix_items_user_id'), table_name='items')
    op.drop_index(op.f('ix_items_key'), table_name='items')
    op.drop_index(op.f('ix_items_category_id'), table_name='items')
    op.drop_table('items')
    op.drop_index(op.f('ix_item_images_key'), table_name='item_images')
    op.drop_index(op.f('ix_item_images_item_id'), table_name='item_images')
    op.drop_table('item_images')
    # ### end Alembic commands ###