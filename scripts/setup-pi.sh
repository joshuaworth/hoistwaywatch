#!/usr/bin/env bash
set -euo pipefail

echo "HoistwayWatch: Raspberry Pi setup"
echo ""
echo "This provisions a Pi for local-first operation (vision → rules → alerts)."
echo "It installs system packages, creates a venv, and prepares systemd units."

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
echo "- Copy/edit configs in ./configs/"
echo "- Install systemd units from ./systemd/ (see docs/field-setup.md)"

