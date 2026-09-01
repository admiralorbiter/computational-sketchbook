.PHONY: dev test fmt lint hooks

VENV?=.venv

dev:
	FLASK_APP=app FLASK_ENV=development flask --app app run --debug

test:
	pytest

fmt:
	black . && isort .

lint:
	flake8 .

hooks:
	pre-commit install
