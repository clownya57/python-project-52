#!/usr/bin/env bash

set -Eeuo pipefail

curl \
  --proto '=https' \
  --proto-redir '=https' \
  --tlsv1.2 \
  -LsSf \
  https://astral.sh/uv/install.sh \
  | sh

source "$HOME/.local/bin/env"

make install \
  && make collectstatic \
  && make migrate
