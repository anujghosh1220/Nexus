import pytest
from app.core.config import settings


def test_settings_load():
    """Test that settings load correctly."""
    assert settings.APP_NAME == "NEXUS"
    assert settings.API_V1_PREFIX == "/api/v1"


def test_cors_origins_parsing():
    """Test that CORS origins are parsed correctly."""
    origins = settings.cors_origins_list
    assert isinstance(origins, list)
    assert len(origins) > 0
