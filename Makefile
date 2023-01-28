.PHONY: test
test:
	poetry run pytest -x -vv src/claydocs tests

.PHONY: lint
lint:
	poetry run flake8 src/claydocs tests

.PHONY: coverage
coverage:
	poetry run pytest --cov-config=pyproject.toml --cov-report html --cov claydocs src/claydocs tests

.PHONY: types
types:
	poetry run pyright src/claydocs

.PHONY: install
install:
	poetry install --with dev,test
	# pre-commit install

.PHONY: theme
theme:
	cd src/theme \
	&& npm run build
