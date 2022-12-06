#!/bin/bash
set -eoux pipefail

python -m pytest src -vv
python -m black --check src
python -m pflake8 src
python -m isort --check src
python -m mypy src
