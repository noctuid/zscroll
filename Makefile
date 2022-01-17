.PHONY: lint
lint:
	$(MAKE) --keep-going pylint flake8 pydocstyle mypy black-check isort-check

.PHONY: pylint
pylint:
	@echo
	@echo "Linting with pylint"
	@poetry run pylint zscroll $(shell pwd)

# pycodestyle and pyflakes
.PHONY: flake8
flake8:
	@echo
	@echo "Linting with flake8 (includes pycodestyle, mccabe, and pyflakes)"
	@poetry run flake8 zscroll .

# TODO does nothing
.PHONY: pydocstyle
pydocstyle:
	@echo
	@echo "Linting with pydocstyle"
	@poetry run pydocstyle zscroll .

.PHONY: mypy
mypy:
	@echo
	@echo "Linting with mypy"
	@poetry run mypy zscroll .

.PHONY: black-check
black-check:
	@echo
	@echo "Checking formatting with black"
	@poetry run black --check zscroll .

.PHONY: black-format
black-format:
	@echo
	@echo "Fixing formatting with black"
	@poetry run black zscroll .

.PHONY: isort-check
isort-check:
	@echo
	@echo "Checking formatting with isort"
	@poetry run isort --check zscroll .

.PHONY: isort-format
isort-format:
	@echo
	@echo "Fixing formatting with isort"
	@poetry run isort zscroll .

.PHONY: format
format:
	@$(MAKE) isort-format black-format

.PHONY: test
test:
	poetry run pytest -s -vv

.PHONY: test-cov
test-cov:
	poetry run pytest -s -vv --cov=zscroll

.PHONY: deps
deps:
	poetry install
