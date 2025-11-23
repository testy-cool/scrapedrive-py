.PHONY: help install install-dev test test-cov lint format type-check clean build publish

help:
	@echo "ScrapeDrive Python SDK - Development Commands"
	@echo ""
	@echo "  install       Install package in production mode"
	@echo "  install-dev   Install package in development mode with all extras"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black"
	@echo "  type-check    Run type checking with mypy"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build distribution packages"
	@echo "  publish       Publish to PyPI (requires credentials)"

install:
	pip install .

install-dev:
	pip install -e ".[dev,async]"

test:
	pytest

test-cov:
	pytest --cov=scrapedrive --cov-report=html --cov-report=term

lint:
	ruff check scrapedrive tests
	black --check scrapedrive tests examples

format:
	black scrapedrive tests examples

type-check:
	mypy scrapedrive

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	twine check dist/*
	twine upload dist/*
