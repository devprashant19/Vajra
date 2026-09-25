import os
import pytest
from alembic.config import Config
from alembic import command
from vajra_core.config.settings import settings

def test_alembic_migrations(tmp_path):
    # Set DB URL to sqlite in tmp_path
    db_path = tmp_path / "test.db"
    os.environ["VAJRA_DATABASE_URL"] = f"sqlite:///{db_path}"
    
    # Needs to reload settings to pickup env vars, or just patch it
    settings.database_url = f"sqlite:///{db_path}"

    alembic_cfg = Config("packages/vajra-core/alembic.ini")
    alembic_cfg.set_main_option("script_location", "packages/vajra-core/alembic")

    # Upgrade to head
    command.upgrade(alembic_cfg, "head")

    # Downgrade to base
    command.downgrade(alembic_cfg, "base")

    # Upgrade back to head
    command.upgrade(alembic_cfg, "head")
    
    assert db_path.exists()
