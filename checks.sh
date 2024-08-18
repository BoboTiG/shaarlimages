#!/bin/bash
set -eu

python -m ruff format host server.py tests
python -m ruff check --fix --unsafe-fixes host server.py
python -m mypy host server.py
python -m mypy tests || true
