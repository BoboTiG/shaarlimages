#!/bin/bash

python -m isort host server.py tests || true
python -m black host server.py tests || true
python -m flake8 host server.py tests || true
# python -m mypy host/*.py server.py tests
