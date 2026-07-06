#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:/root/.local/bin:$PATH"

python3 --version
python3 -m pytest -q
streamlit --version
