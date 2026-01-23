# Contributing to HoistwayWatch

Thanks for helping build a safer, local-first awareness layer for hoistway work.

## What we need most
- **Field feedback**: which zones matter, camera placement, and what alerts are actually useful.
- **Reliability improvements**: anything that reduces false negatives (missed motion) first, then false positives.
- **Docs**: installation/field setup checklists, photos/diagrams (privacy-safe), and troubleshooting notes.

## Ground rules
- **Safety-first**: This project is an *awareness layer*, not an interlock. Avoid claims that imply safety certification.
- **Privacy-first**: Prefer local-only operation; treat recorded video as sensitive.
- **Explainable logic**: Default to simple, auditable rules. If ML is added, it must degrade gracefully.

## How to contribute
1. **Open an issue** describing the change and the intended user impact.
2. **Keep PRs small** and scoped to one improvement when possible.
3. **Add/update docs** whenever behavior or setup changes.

## Development conventions (repo-wide)
- **Line endings**: LF
- **Formatting**: See `.editorconfig`
- **Secrets**: Never commit `.env`, tokens, or private videos.

## Reporting a security issue
Please see `SECURITY.md`.

