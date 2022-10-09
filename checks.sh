#!/bin/bash
set -eoux pipefail

python -m pytest src
python -m black src
python -m pflake8 src
