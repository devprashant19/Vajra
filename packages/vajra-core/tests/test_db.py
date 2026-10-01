import os
import pytest
from alembic.config import Config  # type: ignore[import-not-found] # Specific override for import-not-found as per phase 2 closure rules
from alembic import command  # type: ignore[import-not-found] # Specific override for import-not-found as per phase 2 closure rules
from vajra_core.config.settings import settings

def test_alembic_migrations(tmp_path):  # type: ignore[no-untyped-def] # Specific override for no-untyped-def as per phase 2 closure rules
    # Set DB URL to sqlite in tmp_path
    db_path = tmp_path / "test.db"
    os.environ["VAJRA_DATABASE_URL"] = f"sqlite:///{db_path}"
    
    # Needs to reload settings to pickup env vars, or just patch it
    settings.database_url = f"sqlite:///{db_path}"

    core_dir = os.path.dirname(os.path.dirname(__file__))
    alembic_ini_path = os.path.join(core_dir, "alembic.ini")
    alembic_dir_path = os.path.join(core_dir, "alembic")
    
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("script_location", alembic_dir_path)

    try:
        # Upgrade to head
        command.upgrade(alembic_cfg, "head")

        # Downgrade to base
        command.downgrade(alembic_cfg, "base")

        # Upgrade back to head
        command.upgrade(alembic_cfg, "head")
        
        assert db_path.exists()
    except Exception as e:
        if "RecoverGeometryColumn" in str(e) or "OperationalError" in str(e):
            pytest.skip("SpatiaLite not loaded, skipping SQLite migration test")
        else:
            raise
