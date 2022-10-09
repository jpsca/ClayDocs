.PHONY: test
test:
	pytest -x claydocs tests

.PHONY: lint
lint:
	flake8 --config=setup.cfg claydocs tests

.PHONY: coverage
coverage:
	pytest --cov-config=.coveragerc --cov-report html --cov claydocs claydocs tests

.PHONY: types
types:
	mypy claydocs

.PHONY: install
install:
	pip install -e .[test,dev]
	pip install -r docs/requirements.txt
	# pre-commit install

.PHONY: tailwind
tailwind:
	npx tailwindcss -i ./static/_source.css -o ./static/docs.css --watch