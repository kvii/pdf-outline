.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: freeze
freeze:
	pip freeze > requirements.txt 

.PHONY: test
test:
	python -m unittest

.PHONY: run
run:
	docker compose run --rm app

.PHONY: init
init:
	python -m venv .env