PYTHON := docker-compose run -u $(USERID):$(GROUPID) --rm flask python

up:
	docker-compose up

down:
	docker-compose down

build:
	docker-compose build

build-no-cache:
	docker-compose build --no-cache

db-migrate:
	$(PYTHON) -m flask db migrate -m "${m}"

db-upgrade:
	$(PYTHON) -m flask db upgrade

collect-data:
	$(PYTHON) -m flask collect-data

help:
	$(PYTHON) -m flask --help
