export PYTHONPATH := `pwd`:$(PYTHONPATH)

.PHONY: all
all: lint test

.PHONY: deps
deps:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt

.PHONY: lint
lint:
	flake8 . --count --show-source --statistics --max-line-length=127

.PHONY: test
test:
	pytest --cov-report term --cov=health

devimg=spyglass-devenv
.PHONY: devimage
devimage:
	docker build -f ./Dockerfile.dev -t $(devimg) .

.PHONY: dev
dev: devimage
	docker run -v `pwd`:/app --rm -ti --entrypoint /bin/bash $(devimg)
