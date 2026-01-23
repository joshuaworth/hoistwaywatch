# 📹 HoistwayWatch

**Open-source real-time hoistway awareness for technician safety.**

Most serious incidents aren't mysterious failures. They're moments of uncertainty—unseen movement, unexpected state changes, bad line of sight, wrong assumptions at the worst possible time.

HoistwayWatch provides continuous visibility and real-time alerts for elevator hoistway work using low-cost cameras and simple, explainable detection.

---

## ⚡ Quick Facts

| | |
|---|---|
| **Type** | Safety awareness system |
| **Stack** | Python 3.12 · OpenCV · NATS · Pydantic |
| **Hardware** | Raspberry Pi 5 / Jetson Orin |
| **Status** | 🟡 MVP (vision → rules → alerts working) |
| **License** | Apache 2.0 |

---

## 🎯 What It Does

| Feature | Description |
|---------|-------------|
| 📹 **Zone-based motion detection** | Define car path, pit, overhead zones—alert when motion detected |
| 👁️ **Lighting quality awareness** | Confidence-aware detection that knows when visibility is poor |
| 🚨 **Tamper/occlusion detection** | Alerts if camera is moved, covered, or view is blocked |
| 📋 **Explainable alerts** | Every alert shows exactly what triggered it and why |
| 🔇 **Local-first** | Runs on-site, no cloud required, privacy by default |

---

## ⚠️ Safety Stance

HoistwayWatch is an **awareness layer**, not a safety interlock.

| What it is | What it is NOT |
|------------|----------------|
| Additional visibility aid | Controller override system |
| Real-time motion alerts | Substitute for procedures/training |
| Explainable rule-based detection | Certified safety device |
| Local-first, privacy-respecting | Remote monitoring service |

---

## 🏗️ Architecture

Four microservices communicating via NATS message bus:

| Service | Purpose | Events |
|---------|---------|--------|
| `hw-capture` | Camera health monitoring | `capture.camera_health.v1` |
| `hw-vision` | Motion/tamper/lighting detection | `vision.motion_in_zone.v1`, `vision.tamper_or_occlusion.v1` |
| `hw-rules` | Event → Alert conversion (YAML rules) | Subscribes to all `hw.events.*` |
| `hw-alerts` | Siren/strobe/log output | `hw.alerts.v1` |

**Data Flow:**
```
Camera → hw-capture → NATS → hw-vision → NATS → hw-rules → NATS → hw-alerts → Siren/Strobe
```

---

## 📡 Event Types

| Event | Payload | Use |
|-------|---------|-----|
| `capture.camera_health.v1` | `status`, `latency_ms` | Camera online/offline/stalled |
| `vision.motion_in_zone.v1` | `zone_id`, `motion_score`, `confidence` | Motion detected in zone |
| `vision.person_in_zone.v1` | `zone_id`, `confidence` | Person detected (optional) |
| `vision.lighting_quality.v1` | `quality`, `reason` | Visibility assessment |
| `vision.tamper_or_occlusion.v1` | `status`, `confidence` | Camera tampered/occluded |

---

## 🧰 Hardware Options

| Tier | Hardware | Cameras | Use Case |
|------|----------|---------|----------|
| **Dev** | Raspberry Pi 5 | USB webcam | Prototyping |
| **Jobsite** | Raspberry Pi 5 + PoE hat | 1-2 IP cameras | Field testing |
| **Production** | Jetson Orin Nano/NX | 1-4 PoE cameras | Full deployment |

**Output devices:** Speaker + strobe for audible/visual alerts

---

## 📋 Rules Engine

YAML-configurable rules with correlation support:

```yaml
- id: "R100.motion_with_person_recent"
  when:
    event_type: "vision.motion_in_zone.v1"
    zone_id: "car_path"
    motion_score_gte: 0.15
    and_recent:
      - event_type: "vision.person_in_zone.v1"
        zone_id: "car_path"
        within_sec: 2.0
  then:
    severity: "critical"
    hazard_score: 100
    summary: "Motion detected while person present"
    recommended_action: "Immediate stop. Verify person location."
```

| Feature | Description |
|---------|-------------|
| `zone_id` filter | Match specific zones |
| `motion_score_gte` | Threshold for motion magnitude |
| `confidence_gte` | Minimum visibility confidence |
| `and_recent` | Require supporting events within time window |
| `cooldown_sec` | Prevent alert floods |

---

## 📁 Project Structure

```
hoistwaywatch/
├── src/hoistwaywatch/
│   ├── capture/cli.py      # Camera health service
│   ├── vision/cli.py       # Motion detection service
│   ├── rules/              # Rules engine + state
│   ├── alerts/cli.py       # Alert output service
│   ├── bus/nats_bus.py     # NATS messaging
│   ├── contracts/          # Pydantic models (events, alerts)
│   └── observability/      # JSON structured logging
├── configs/
│   ├── rules.yaml          # Example rules
│   └── example-zones.json  # Zone polygon definitions
├── schemas/                # JSON Schema definitions
├── docs/                   # Safety, architecture, deployment
├── scripts/                # Pi/Jetson setup scripts
└── tests/                  # pytest coverage
```

---

## 🚀 Quick Start

**1. Install**
```bash
make bootstrap
```

**2. Start NATS** (jobsite devices run locally)
```bash
nats-server
```

**3. Run the pipeline**
```bash
hw-alerts &
hw-rules --rules configs/rules.yaml &
hw-vision --source 0 --zones configs/example-zones.json
```

Motion in a defined zone → rule triggers → alert fires.

---

## 🛠️ Dev Commands

| Command | Description |
|---------|-------------|
| `make bootstrap` | Install dependencies |
| `make lint` | Run ruff |
| `make test` | Run pytest |
| `make ci` | Full CI check |

---

## 🛣️ Roadmap

| Version | Features |
|---------|----------|
| **v0.1** ✅ | Zone motion detection, rules engine, local alerts |
| **v0.2** | Person detection (YOLO), multi-camera, low-light handling |
| **v0.3** | Portable jobsite kit, calibration tools, mobile companion |

---

## 🔒 Privacy

- **Local-only by default** — no cloud, no external connections
- **Recording optional** — off by default
- **Centralized logging** — opt-in module for orgs that want it

---

## 🤝 Contributing

Looking for:
- Field feedback on zone placement
- Camera angle guidance from actual techs
- Edge-case test scenarios
- Reliability improvements

---

## 📜 License

Apache 2.0
