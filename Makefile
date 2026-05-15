# Development Tasks

.PHONY: help install install-dev test test-cov lint format type-check clean docs run-example

help:
	@echo "Identity Risk Scoring Engine - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          - Install dependencies"
	@echo "  make install-dev      - Install with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make test             - Run test suite"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make lint             - Run linters (flake8, pylint)"
	@echo "  make format           - Format code with black"
	@echo "  make type-check       - Run mypy type checking"
	@echo "  make clean            - Remove build artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make run-basic        - Run basic usage example"
	@echo "  make run-advanced     - Run advanced scenario example"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs             - Build documentation"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	flake8 src/ tests/ examples/ --max-line-length=100
	pylint src/risk_engine --disable=C0111,R0913

format:
	black src/ tests/ examples/ --line-length=100

type-check:
	mypy src/risk_engine --ignore-missing-imports

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info
	rm -rf htmlcov/ .coverage
	rm -rf .mypy_cache/ .pytest_cache/

run-basic:
	@echo "Running basic usage example..."
	PYTHONPATH=src python examples/basic_usage.py

run-advanced:
	@echo "Running advanced scenario example..."
	PYTHONPATH=src python examples/advanced_scenario.py

docs:
	@echo "Building documentation..."
	@echo "Documentation files: README.md, ARCHITECTURE.md, SECURITY.md"

.PHONY: docker-build docker-run docker-clean
docker-build:
	docker build -t identity-risk-scoring-engine .

docker-run:
	docker run -p 8000:8000 identity-risk-scoring-engine

docker-clean:
	docker rmi identity-risk-scoring-engine
