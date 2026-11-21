import json

import pytest

from relay import create_service


@pytest.fixture
def profile(tmp_path, monkeypatch):
    settings = tmp_path / "profile.json"
    settings.write_text('{"mode": "serving"}', encoding="utf-8")
    monkeypatch.setenv("RELAY_STATE_FILE", str(settings))
    monkeypatch.setenv("RELAY_REVISION", "candidate.6")
    return settings


@pytest.mark.parametrize(
    ("mode", "expected"),
    [("serving", 200), ("maintenance", 503)],
)
def test_health_response(profile, mode, expected):
    profile.write_text(json.dumps({"mode": mode}), encoding="utf-8")
    response = create_service().test_client().get("/health")
    assert response.status_code == expected
    assert response.json == {"mode": mode}


def test_revision_reflects_environment(profile):
    response = create_service().test_client().get("/version")
    assert response.status_code == 200
    assert response.json == {"revision": "candidate.6"}


@pytest.mark.parametrize("invalid", ["broken", "[]", "{}", '{"mode": "unknown"}'])
def test_invalid_profile_stops_startup(profile, invalid):
    profile.write_text(invalid, encoding="utf-8")
    with pytest.raises(ValueError):
        create_service()


@pytest.mark.parametrize("invalid", ["  ", "branch/name"])
def test_invalid_revision_stops_startup(profile, monkeypatch, invalid):
    monkeypatch.setenv("RELAY_REVISION", invalid)
    with pytest.raises(ValueError, match="Invalid revision label"):
        create_service()


def test_version_content_type(profile):
    response = create_service().test_client().get("/version")
    assert response.mimetype == "application/json"
