PYTHON := docker-compose run -u $(USERID):$(GROUPID) --rm flask python

up:
	docker-compose up

down:
	docker-compose down

build:
	docker-compose build

build-no-cache:
	docker-compose build --no-cache

db-upgrade:
	$(PYTHON) -m flask db upgrade
