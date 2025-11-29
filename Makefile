# Makefile for rfid-r200 Python package using uv
# Provides convenient commands for development, testing, building, and publishing

.PHONY: help install install-dev test test-verbose type-check format lint clean build build-check upload-test publish check

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install package from source (editable mode)"
	@echo "  install-dev  Install package with development dependencies"
	@echo "  test         Run tests"
	@echo "  test-verbose Run tests with verbose output"
	@echo "  test-cov     Run tests with coverage"
	@echo "  type-check   Run mypy type checking"
	@echo "  format       Format code with black"
	@echo "  lint         Run code linting with flake8"
	@echo "  clean        Clean build artifacts and cache files"
	@echo "  build        Build source and wheel distributions"
	@echo "  build-check  Check if build is valid"
	@echo "  upload-test  Upload to Test PyPI"
	@echo "  publish      Upload to PyPI"
	@echo "  check        Run all quality checks before publishing"

# Installation using uv
install:
	uv pip install -e .

install-dev:
	uv pip install -e .[dev,test]
	uv sync --group dev

# Testing
test:
	uv run pytest

test-verbose:
	uv run pytest -v

test-cov:
	uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Code quality
type-check:
	uv run mypy src --ignore-missing-imports

format:
	uv run black src tests

lint:
	uv run flake8 src tests --max-line-length=120

check: type-check format lint test

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Building using uv
build: clean
	uv tool run --from build pyproject-build

build-check: build
	uv tool run twine check dist/*

# Publishing
upload-test: build
	uv tool run twine upload --repository testpypi dist/*

publish: build
	uv tool run twine upload dist/*

# Development workflow using uv
dev-setup: install-dev
	@echo "Setting up pre-commit hooks..."
	uv tool install pre-commit --with pre-commit-uv
	uv run pre-commit install || echo "Pre-commit installation failed, but continuing..."

# Full quality check before publishing
pre-publish: clean check build-check
	@echo "✅ All checks passed! Ready to publish."
	@echo "To publish to test PyPI, run: make upload-test"
	@echo "To publish to PyPI, run: make publish"

# Quick development cycle using uv
dev: format type-check test
	@echo "✅ Development cycle completed!"

# Continuous integration targets
ci: type-check test build-check
	@echo "✅ CI pipeline completed successfully!"

# Version management
show-version:
	@uv run python -c "import sys; sys.path.insert(0, 'src'); import rfid_r200; print(rfid_r200.__version__)"

# Dependencies management using uv
update-deps:
	uv pip install --upgrade build twine black mypy pytest flake8 pytest-cov
	uv sync

# Documentation
docs:
	@echo "Documentation is available in README.md and docs/"
	@echo "To view locally: uv run python -m http.server 8000 --directory docs"

# Package verification
verify:
	@echo "Verifying package structure..."
	@uv run python -c "import sys; sys.path.insert(0, 'src'); import rfid_r200; print('✓ Package imports successfully')"
	@uv run python -c "import sys; sys.path.insert(0, 'src'); from rfid_r200 import R200, AsyncR200; print('✓ Main classes available')"
	@uv run python -c "import sys; sys.path.insert(0, 'src'); from rfid_r200 import __version__; print(f'✓ Version: {__version__}')"
	@echo "✓ Package structure verified!"

# PyPI verification
check-pypi:
	@echo "Checking if package name is available on PyPI..."
	@curl -s "https://pypi.org/simple/rfid-r200/" | grep -q "rfid-r200" && echo "⚠️  Package already exists on PyPI" || echo "✅ Package name is available on PyPI"

# Git helpers
git-tag:
	@read -p "Enter version to tag: " version; \
	git tag -a "v$$version" -m "Release version $$version"
	@echo "Tag v$$version created. Push with: git push --tags"

git-push-tag:
	@read -p "Enter version tag to push: " tag; \
	git push origin $$tag

# Quick shortcuts
c: clean
t: test
b: build
p: publish

# Advanced development commands
dev-all: clean install-dev format type-check test-cov
	@echo "✅ Full development cycle completed!"

# Release workflow
release: clean check build-check
	@echo "🚀 Ready for release!"
	@echo "Choose one of the following:"
	@echo "  make upload-test  # Upload to Test PyPI"
	@echo "  make publish      # Upload to production PyPI"

# Local testing before publishing
local-test: clean build
	@echo "Testing local build..."
	@uv pip uninstall -y rfid-r200 2>/dev/null || true
	@uv pip install dist/*.whl --force-reinstall
	@uv run python -c "import rfid_r200; print('✅ Local package installation successful!')"
