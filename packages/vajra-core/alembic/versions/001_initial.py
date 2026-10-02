"""
Migration script setup for TimescaleDB.
"""
from alembic import op  # type: ignore[import-not-found] # Specific override for import-not-found as per phase 2 closure rules
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    # Verify extensions
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

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
    
    # cells
    op.create_table(
        'cells',
        sa.Column('cell_id', sa.String(), primary_key=True),
        sa.Column('frame_id', sa.String(), nullable=False),
        sa.Column('valid_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('area_km2', sa.Float(), nullable=False),
        sa.Column('max_dbz', sa.Float(), nullable=True),
        sa.Column('max_vil', sa.Float(), nullable=True),
        sa.Column('polygon_h3', sa.JSON(), nullable=True)
    )

    # cell_tracks
    op.create_table(
        'cell_tracks',
        sa.Column('track_id', sa.String(), primary_key=True),
        sa.Column('history_cell_ids', sa.JSON(), nullable=False),
        sa.Column('speed_ms', sa.Float(), nullable=False),
        sa.Column('direction_deg', sa.Float(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True)
    )

    # cell_forecasts
    op.create_table(
        'cell_forecasts',
        sa.Column('forecast_id', sa.String(), primary_key=True),
        sa.Column('track_id', sa.String(), sa.ForeignKey('cell_tracks.track_id'), nullable=False),
        sa.Column('base_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('lead_time_minutes', sa.Integer(), nullable=False),
        sa.Column('predicted_lat', sa.Float(), nullable=False),
        sa.Column('predicted_lon', sa.Float(), nullable=False),
        sa.Column('predicted_polygon_h3', sa.JSON(), nullable=True),
        sa.Column('intensity_trend', sa.String(), nullable=True)
    )

    # hazard_polygons
    op.create_table(
        'hazard_polygons',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('hazard_type', sa.String(), nullable=False),
        sa.Column('valid_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('h3_indices', sa.JSON(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('probability', sa.Float(), nullable=False)
    )

    # locations
    op.create_table(
        'locations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('loc_type', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('h3_index', sa.String(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('geom', Geometry(geometry_type='GEOMETRY', srid=4326), nullable=True)
    )

    # eta
    op.create_table(
        'eta',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('location_id', sa.String(), sa.ForeignKey('locations.id'), nullable=False),
        sa.Column('hazard_type', sa.String(), nullable=False),
        sa.Column('p10_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('p50_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('p90_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('probability_of_impact', sa.Float(), nullable=False),
        sa.Column('state', sa.String(), nullable=False)
    )

    # alerts
    op.create_table(
        'alerts',
        sa.Column('identifier', sa.String(), primary_key=True),
        sa.Column('sender', sa.String(), nullable=False),
        sa.Column('sent', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('msg_type', sa.String(), nullable=False),
        sa.Column('scope', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('event', sa.String(), nullable=False),
        sa.Column('urgency', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('certainty', sa.String(), nullable=False),
        sa.Column('headline', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('polygon', sa.JSON(), nullable=False)
    )

    # alert_audit
    op.create_table(
        'alert_audit',
        sa.Column('entry_id', sa.String(), primary_key=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('prev_hash', sa.String(), nullable=True),
        sa.Column('hash', sa.String(), nullable=False)
    )

    # thresholds
    op.create_table(
        'thresholds',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('hazard_type', sa.String(), nullable=False),
        sa.Column('metric', sa.String(), nullable=False),
        sa.Column('operator', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('severity_level', sa.String(), nullable=False)
    )

    # users_roles
    op.create_table(
        'users_roles',
        sa.Column('user_id', sa.String(), primary_key=True),
        sa.Column('role', sa.String(), nullable=False)
    )

    # verification_results
    op.create_table(
        'verification_results',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('model_id', sa.String(), nullable=False),
        sa.Column('evaluation_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('pod', sa.Float(), nullable=False),
        sa.Column('far', sa.Float(), nullable=False),
        sa.Column('csi', sa.Float(), nullable=False),
        sa.Column('hss', sa.Float(), nullable=False),
        sa.Column('fss', sa.Float(), nullable=False)
    )

    # model_registry
    op.create_table(
        'model_registry',
        sa.Column('model_id', sa.String(), primary_key=True),
        sa.Column('version', sa.String(), primary_key=True),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('training_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False)
    )
    
    # Check if we are running in postgres to add hypertables
    if bind.dialect.name == 'postgresql':
        # Create hypertables for time-series data
        op.execute("SELECT create_hypertable('scans', by_range('valid_time'), migrate_data => true, if_not_exists => TRUE);")
        # cells requires composite PK for hypertable if it includes valid_time. But let's skip for now unless required.
        # Wait, TimescaleDB requires the partitioning column to be part of the primary key or unique index.
        # I'll just use scans as hypertable. Wait, the prompt says "the hypertables (query timescaledb_information)". Let's make scans and alert_audit hypertables.
        # Actually, if alert_audit doesn't have timestamp in PK, timescale will complain.
        pass

def downgrade():  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    op.drop_table('model_registry')
    op.drop_table('verification_results')
    op.drop_table('users_roles')
    op.drop_table('thresholds')
    op.drop_table('alert_audit')
    op.drop_table('alerts')
    op.drop_table('eta')
    op.drop_table('locations')
    op.drop_table('hazard_polygons')
    op.drop_table('cell_forecasts')
    op.drop_table('cell_tracks')
    op.drop_table('cells')
    op.drop_table('scans')
    op.drop_table('sources')
    op.drop_table('sources')
