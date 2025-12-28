# HoistwayWatch 📹⚠️  
Open-source real-time hoistway awareness for technician safety

Most serious incidents are not mysterious failures. They are moments of uncertainty: unseen movement, unexpected state changes, bad line of sight, or wrong assumptions at the worst possible time.

HoistwayWatch is an open-source project to provide 📹 continuous visibility 📹 and real-time alerts for elevator hoistway work using low-cost cameras plus simple, explainable detection.

This is not meant to replace existing safety practices. It adds real-time awareness so fewer hazards become surprises.

## Goals 🎯
- Real-time hoistway awareness with inexpensive hardware
- Detect motion and unsafe conditions and alert immediately
- Keep logic auditable, simple, and explainable
- Run locally on-site (privacy-first)
- Work vendor-neutral and avoid proprietary controller integration for the MVP

## Non-goals 🚫
- This is not a controller override system
- This is not a substitute for proper procedures, training, or codes
- This is not a remote monitoring service by default
- This project does not provide OEM-specific instructions

## Core concept 🧠
A camera watches the hoistway zones that matter. The system detects:
- Car movement (or any movement in defined zones)
- Human presence in defined danger zones (optional)
- Door zone changes (optional)
- Unusual motion patterns (optional)
- “Movement while someone is present in the hoistway” style rules

Then it triggers:
- Local audible alarm
- Flashing strobe
- Phone notification (local network)
- Event log for review

## MVP features ✅
### 1) Continuous visibility
- One or more cameras with a simple live dashboard
- Timestamped recording optional

### 2) Motion detection with zones
- Define regions of interest (ROI) for “car path”, “counterweight path”, “pit”, “overhead”
- Trigger alert when motion occurs in a zone

### 3) Presence detection (optional)
- Detect a person in a defined zone
- Trigger stronger alert if motion happens while presence is detected

### 4) Local-first alerting
- On-device alarms
- Local network notifications
- No cloud required

### 5) Explainable rules engine
- Rules are simple JSON or YAML
- Every alert explains exactly what triggered it

## Safety stance ⚠️
HoistwayWatch is an awareness layer, not a safety interlock.  
It should be used only as an additional aid with proper training and procedures.

If you want a safety interlock system, that requires a totally different engineering and certification path.

## Hardware options 🧰
### Lowest cost
- Raspberry Pi 5 or Pi 4
- 1 to 2 USB cameras or PoE IP camera
- Small powered speaker + strobe
- Optional local Wi-Fi router (jobsite isolated network)

### Best practical “site ready”
- NVIDIA Jetson Orin Nano or Orin NX
- 1 to 4 PoE IP cameras
- PoE switch
- Speaker + strobe
- Rugged case

### Sensors (optional add-ons)
- Simple vibration sensor
- Magnetic door switch for access points
- IR beam for doorway presence

## Software architecture 🏗️
### Components
- `hw-capture`  
  Camera ingest (RTSP for IP cams, UVC for USB cams)

- `hw-vision`  
  Motion detection and optional object detection

- `hw-rules`  
  A small rules engine that evaluates events like:
  - motion_in_zone
  - person_in_zone
  - motion_and_person
  - camera_offline
  - low_light

- `hw-alerts`  
  Audible, strobe, push notifications (local), event log

- `hw-ui`  
  Local dashboard showing live feeds, zones, and alert history

### ML approach 🤖
Start with simple, robust primitives:
- Motion detection (frame differencing, background subtraction)
- Zone-based triggering
- Optional person detector (YOLO or MobileNet) running locally

Design rule: If the ML fails, the system still provides continuous visibility.

## Repo layout 📁
```
hoistwaywatch/
  README.md
  docs/
    safety.md
    hardware.md
    installation.md
    field-setup.md
    faq.md
  apps/
    dashboard/         # web UI
  services/
    capture/           # camera ingest
    vision/            # motion + detection
    rules/             # event rules engine
    alerts/            # audio/strobe/notify
  configs/
    example-site.yaml
    example-zones.json
  scripts/
    setup-pi.sh
    setup-jetson.sh
  licenses/
```

## Documentation 📚
Start with:
- `docs/safety.md`
- `docs/privacy.md`
- `docs/field-setup.md`
- `docs/architecture.md`
- `docs/deployment.md`

## Quick start 🚀
### Step 1: Run locally (dev)
This MVP is real and runnable: **vision → rules → alerts**.

```bash
make bootstrap
```

Bring up a local NATS server (jobsite devices run it locally), then run:
```bash
hw-alerts
hw-rules --rules configs/rules.yaml
hw-vision --source 0 --zones configs/example-zones.json
```

### Step 2: Jobsite prototype
- Use an isolated Wi-Fi router
- Place camera where it can see the critical path
- Add a speaker and strobe
- Validate “movement equals alert” works every time

## Field setup guidance 👷‍♂️
The system is only as good as camera placement. The MVP guidance:
- Favor angles that show the car path clearly
- Avoid direct glare and strong reflections
- Add a second camera for pits and overheads when possible
- Prefer fixed mounts and stable reference points
- The goal is not pretty video. The goal is clarity under real conditions

## Privacy 🔒
- Default mode is local-only
- Recording is optional and off by default
- No cloud upload by default
- If an org wants centralized logging, it’s an opt-in module

## Roadmap 🛣️
### v0.1 (MVP)
- Live view dashboard
- Zones + motion detection
- Local alerts
- Event logging

### v0.2
- Optional person detection
- Multi-camera support
- Better low-light handling

### v0.3
- Portable “jobsite kit” reference build
- Better calibration tools
- Offline-first mobile companion view

### Future
- Integrations that are vendor-neutral (not controller-specific) where feasible
- Formal validation guidance for organizations that want to adopt responsibly

## How to contribute 🤝
We want:
- Field feedback on what zones matter
- Camera placement guidance from actual installers and service techs
- Edge-case videos (with privacy-safe handling)
- Simple improvements that increase reliability

## License 📜
Recommended: Apache 2.0 (permissive, safe for broad adoption).
