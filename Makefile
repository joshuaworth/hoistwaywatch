.PHONY: help bootstrap lint test ci

help:
	@echo "HoistwayWatch (scaffold)"
	@echo ""
	@echo "Targets:"
	@echo "  make bootstrap - install dev dependencies"
	@echo "  make lint      - run ruff"
	@echo "  make test      - run pytest"
	@echo "  make ci    - run repo hygiene checks"

bootstrap:
	@python3 -m pip install -U pip
	@python3 -m pip install -e ".[dev]"

lint: bootstrap
	@python3 -m ruff check .

test: bootstrap
	@python3 -m pytest

ci:
	@./scripts/ci/ci.sh

