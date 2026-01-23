#!/usr/bin/env bash
set -euo pipefail

echo "HoistwayWatch: Jetson setup"
echo ""
echo "This provisions a Jetson for local-first operation (vision → rules → alerts)."
echo "Assumes Ubuntu + JetPack is already installed."

sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
  python3 python3-venv python3-pip \
  ca-certificates curl jq \
  nats-server \
  libglib2.0-0 libgl1

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"

echo ""
echo "Next:"
echo "- Configure camera source + zones"
echo "- Install systemd units from ./systemd/"

