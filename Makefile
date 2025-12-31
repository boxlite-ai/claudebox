.PHONY: build-image publish-image install test lint format clean help

# Configuration
IMAGE := ghcr.io/boxlite-labs/claudebox-runtime
VERSION := $(shell grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2)

help:
	@echo "ClaudeBox"
	@echo ""
	@echo "Docker:"
	@echo "  make build-image    Build runtime image"
	@echo "  make publish-image  Publish to ghcr.io"
	@echo ""
	@echo "Python:"
	@echo "  make install        Install in dev mode"
	@echo "  make test           Run tests"
	@echo "  make lint           Lint code"
	@echo "  make format         Format code"
	@echo "  make clean          Clean artifacts"

# Docker
build-image:
	docker build -t $(IMAGE):$(VERSION) -t $(IMAGE):latest -f image/Dockerfile image/

publish-image: build-image
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest

# Python
install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

lint:
	ruff check src/

format:
	ruff format src/ examples/

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .ruff_cache/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
