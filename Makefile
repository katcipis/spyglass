export PYTHONPATH := $(shell pwd)/src

.PHONY: all
all: lint test

.PHONY: deps
deps:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt

.PHONY: lint
lint:
	flake8 . --count --show-source --statistics

.PHONY: test
test:
	pytest ./tests/unit --cov-report term --cov=health

.PHONY: test-setup
test-setup:
	python setup.py check

.PHONY: test-setup
setup-database:
	./tools/setup-database

.PHONY: test-integration
test-integration:
	# WHY: There is a lot of warnings from aiokafka :-(
	# So I disabled warnings details on pytest.
	pytest ./tests/integration -rs --cov-report term --cov=health --disable-pytest-warnings

devimg=spyglass-devenv
.PHONY: devimage
devimage:
	docker build -f ./Dockerfile.dev -t $(devimg) .

.PHONY: dev
dev: devimage
	docker run -v `pwd`:/app --rm -ti --entrypoint /bin/bash $(devimg)
