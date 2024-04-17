.PHONY: fmt lint test deps deps-dev run-server run-client
.PHONY: docker-build-frontend docker-push-frontend docker-build-backend docker-push-backend

GIT = git
IMAGE_NAME ?= registry/merlin
FRONTEND_IMAGE_NAME := $(IMAGE_NAME)/frontend
BACKEND_IMAGE_NAME := $(IMAGE_NAME)/backend
COMMIT := $(shell $(GIT) rev-parse HEAD)
VERSION ?= $(shell $(GIT) describe --tags ${COMMIT} 2> /dev/null || echo "$(COMMIT)")
TOFMT_FILES := $(shell find -iname \*.py -not \( \
-path \*migrations\* \
-or -path ./.git/\* \
-or -path ./venv/\* \) )

deps:
	pip install -r requirements.txt
	cd frontend && pnpm i

deps-dev: deps
	pip install -r requirements_dev.txt
	cd frontend && pnpm i

fmt:
	python -m isort $(TOFMT_FILES)
	python -m black $(TOFMT_FILES)
	cd frontend && pnpm format

lint:
	python -m flake8
	cd frontend && pnpm lint

test:
	python manage.py test --noinput

run-server:
	DJANGO_SETTINGS_MODULE=merlin.settings.development python manage.py runserver

run-client:
	cd frontend && pnpm dev -o

docker-build-frontend:
	cd frontend && docker build --tag $(FRONTEND_IMAGE_NAME):$(VERSION) .
	docker tag $(FRONTEND_IMAGE_NAME):$(VERSION) $(FRONTEND_IMAGE_NAME):latest

docker-push-frontend:
	docker push $(FRONTEND_IMAGE_NAME):$(VERSION)
	docker push $(FRONTEND_IMAGE_NAME):latest

docker-build-backend:
	docker build --tag $(BACKEND_IMAGE_NAME):$(VERSION) .
	docker tag $(BACKEND_IMAGE_NAME):$(VERSION) $(BACKEND_IMAGE_NAME):latest

docker-push-backend:
	docker push $(BACKEND_IMAGE_NAME):$(VERSION)
	docker push $(BACKEND_IMAGE_NAME):latest
