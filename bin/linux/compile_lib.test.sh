#!/bin/bash
python3.12 -m uv pip compile --extra test app/pyproject.toml > app/requirements.lock