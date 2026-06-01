# FlowSync SaaS Metrics Agent — Makefile
# Usage: make <target>

.PHONY: help data validate test dashboard clean

help:
	@echo "FlowSync Metrics Agent"
	@echo ""
	@echo "Targets:"
	@echo "  make data       — Regenerate synthetic_data.json (seed=42, 24 months)"
	@echo "  make validate   — Validate synthetic_data.json against schema"
	@echo "  make test       — Run all Python tests"
	@echo "  make dashboard  — Open dashboard in default browser"
	@echo "  make deck       — Open executive deck in default browser"
	@echo "  make serve      — Serve dashboard on http://localhost:8080"
	@echo "  make clean      — Remove __pycache__ and .pyc files"

data:
	@echo "→ Generating synthetic data..."
	python3 agent/data_generator.py --months 24 --seed 42 --output data/synthetic_data.json
	cp data/synthetic_data.json dashboard/assets/data/metrics.json
	@echo "✓ Data generated and copied to dashboard/assets/data/"

validate:
	@echo "→ Validating schema..."
	python3 agent/schema.py data/synthetic_data.json

test:
	@echo "→ Running tests..."
	python3 agent/tests/test_data_generator.py
	python3 agent/tests/test_metrics_calculator.py

dashboard:
	open dashboard/index.html 2>/dev/null || xdg-open dashboard/index.html

deck:
	open docs/executive_deck.html 2>/dev/null || xdg-open docs/executive_deck.html

serve:
	@echo "→ Serving on http://localhost:8080"
	python3 -m http.server 8080 --directory .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cleaned"
