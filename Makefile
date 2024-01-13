.PHONY: fmt lint set-hooks test  deps deps-dev run-server run-client

GIT = git
COMMIT := $(shell $(GIT) rev-parse HEAD)
VERSION ?= $(shell $(GIT) describe --tags ${COMMIT} 2> /dev/null || echo "$(COMMIT)")
TOFMT_FILES := $(shell find -iname \*.py -not \( \
-path \*migrations\* \
-or -path ./.git/\* \
-or -path ./venv/\* \) )

deps:
	pip install -r requirements.txt

deps-dev: deps
	pip install -r requirements_dev.txt

fmt:
	python -m isort $(TOFMT_FILES)
	python -m black $(TOFMT_FILES)

lint:
	python -m flake8

test:
	python manage.py test --noinput

run-server:
	python manage.py runserver

run-client:
	cd frontend && npm run start
