#!/bin/bash
set -eoux pipefail

python -m pytest src -vv
python -m black --check src
python -m flake8 src
