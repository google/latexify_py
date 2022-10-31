#!/bin/bash
set -eoux pipefail

python -m pytest src -vv
python -m black --check src
python -m pflake8 src
