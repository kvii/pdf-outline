.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: freeze
freeze:
	pip freeze > requirements.txt 

.PHONY: test
test:
	python -m unittest