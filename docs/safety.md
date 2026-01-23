# Safety stance

HoistwayWatch is an **awareness layer** (visibility + alerts). It is **not** a safety interlock, controller override, or substitute for training, procedures, codes, or supervision.

## Design principles
- **Local-first**: Operate on-site; avoid unnecessary data egress.
- **Fail-soft**: If detection fails, the user still has live visibility; if a camera fails, it becomes explicit and noisy.
- **Explainable**: Alerts must clearly state the trigger (what zone, what signal, what rule).
- **Bias to safety**: Prefer false positives over false negatives when uncertainty is unavoidable.

## Operational assumptions
- Users follow all applicable codes, OEM guidance, and employer safety procedures.
- Camera placement and validation are part of every deployment.

## What HoistwayWatch must never claim
- That it prevents incidents by itself
- That it is a certified safety device
- That it replaces lockout/tagout, barricades, or required attendants

