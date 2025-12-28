# Installation (prototype → jobsite)

This repo includes a real MVP pipeline you can run locally:
**vision → rules → alerts**, wired via a local NATS event bus.

## Prototype (single camera)
### 1) Install
```bash
python3 -m pip install -U pip
python3 -m pip install -e ".[dev]"
```

### 2) Start NATS (local)
Install NATS on your host (or run it in Docker in production). For dev, you can run `nats-server` if installed.

### 3) Run services
In three terminals:
```bash
hw-alerts --nats nats://127.0.0.1:4222
```
```bash
hw-rules --nats nats://127.0.0.1:4222 --rules configs/rules.yaml
```
```bash
hw-vision --nats nats://127.0.0.1:4222 --source 0 --zones configs/example-zones.json
```

### 4) Validate
- Move in the `car_path` region and confirm an alert prints and is appended to `alerts.ndjson`.

## Jobsite prototype checklist
- Isolated local network (optional but recommended)
- Fixed camera placement
- Audible + visual alerting
- Clear “camera offline” behavior
- Validate at start of shift and after any camera movement

