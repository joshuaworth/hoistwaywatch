# Deployment

HoistwayWatch is designed to run **fully local** on a jobsite edge device.

## Option A: systemd (recommended for field kits)
Assumptions:
- Repo installed at `/opt/hoistwaywatch`
- Python venv at `/opt/hoistwaywatch/.venv`
- Configs in `/opt/hoistwaywatch/configs/`

Steps (high level):
1. Provision the device (see `scripts/setup-pi.sh` or `scripts/setup-jetson.sh`)
2. Copy unit files from `systemd/` into `/etc/systemd/system/`
3. Enable/start:
   - `hoistwaywatch-nats.service`
   - `hoistwaywatch-capture.service`
   - `hoistwaywatch-vision.service`
   - `hoistwaywatch-rules.service`
   - `hoistwaywatch-alerts.service`

## Option B: Docker Compose (portable)
See `deploy/docker-compose.yml`.

Notes:
- Use host networking only if you must; otherwise keep services on an isolated docker network.
- Mount configs read-only.
- Mount `/var/lib/hoistwaywatch` (or equivalent) for logs/evidence.

