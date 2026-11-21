import json
import os
import re
from pathlib import Path

from flask import Flask, jsonify


def create_service():
    revision = os.getenv("RELAY_REVISION", "local").strip()
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}", revision):
        raise ValueError("Invalid revision label")

    profile = Path(os.getenv("RELAY_STATE_FILE", "release-profile.json"))
    try:
        state = json.loads(profile.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError("Invalid release profile") from error
    if not isinstance(state, dict) or state.get("mode") not in ("serving", "maintenance"):
        raise ValueError("Release mode must be serving or maintenance")

    app = Flask(__name__)
    mode = state["mode"]

    @app.get("/health")
    def health():
        return jsonify(mode=mode), 200 if mode == "serving" else 503

    @app.get("/version")
    def version():
        return jsonify(revision=revision)

    return app
