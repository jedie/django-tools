SHELL := /bin/bash
MAX_LINE_LENGTH := 119
POETRY_VERSION := $(shell poetry --version 2>/dev/null)

help: ## List all commands
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9 -]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-poetry:
	@if [[ "${POETRY_VERSION}" == *"Poetry"* ]] ; \
	then \
		echo "Found ${POETRY_VERSION}, ok." ; \
	else \
		echo 'Please install poetry first, with e.g.:' ; \
		echo 'make install-poetry' ; \
		exit 1 ; \
	fi

install-poetry: ## install or update poetry
	@if [[ "${POETRY_VERSION}" == *"Poetry"* ]] ; \
	then \
		echo 'Update poetry v$(POETRY_VERSION)' ; \
		poetry self update ; \
	else \
		echo 'Install poetry' ; \
		curl -sSL "https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py" | python3 ; \
	fi

install: check-poetry ## install django-tools via poetry
	poetry install

update: check-poetry ## update the sources and installation
	git fetch --all
	git pull origin main
	poetry update

lint: ## Run code formatters and linter
	poetry run darker --diff --check
	poetry run flake8 django_tools django_tools_test_project

fix-code-style: ## Fix code formatting
	poetry run darker
	poetry run flake8 django_tools django_tools_test_project

tox-listenvs: check-poetry ## List all tox test environments
	poetry run tox --listenvs

tox: check-poetry ## Run pytest via tox with all environments
	poetry run tox

tox-py37: check-poetry ## Run pytest via tox with *python v3.7*
	poetry run tox -e py37

tox-py38: check-poetry ## Run pytest via tox with *python v3.8*
	poetry run tox -e py38

tox-py39: check-poetry ## Run pytest via tox with *python v3.9*
	poetry run tox -e py39

pytest: check-poetry ## Run pytest
	poetry run pytest

update-rst-readme: ## update README.rst from README.creole
	poetry run update_rst_readme

publish: ## Release new version to PyPi
	poetry run publish

start-dev-server: ## Start Django dev. server with the test project
	DJANGO_SETTINGS_MODULE=django_tools_test_project.settings.local poetry run dev_server


.PHONY: help install lint fix test publish
