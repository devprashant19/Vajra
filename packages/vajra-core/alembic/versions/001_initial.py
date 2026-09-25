"""
Migration script setup for TimescaleDB.
"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # sources
    op.create_table(
        'sources',
        sa.Column('source_id', sa.String(), primary_key=True),
        sa.Column('group_name', sa.String(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True)
    )
    
    # scans
    op.create_table(
        'scans',
        sa.Column('scan_id', sa.String(), primary_key=True),
        sa.Column('source_id', sa.String(), sa.ForeignKey('sources.source_id'), nullable=False),
        sa.Column('valid_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('zarr_url', sa.String(), nullable=False)
    )
    
    # Check if we are running in postgres to add hypertables
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("SELECT create_hypertable('scans', 'valid_time', if_not_exists => TRUE);")

def downgrade():
    op.drop_table('scans')
    op.drop_table('sources')
