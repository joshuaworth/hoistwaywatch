.PHONY: help ci

help:
	@echo "HoistwayWatch (scaffold)"
	@echo ""
	@echo "Targets:"
	@echo "  make ci    - run repo hygiene checks"

ci:
	@./scripts/ci/ci.sh

