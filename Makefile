ENV = env
PYBIN = $(ENV)/scripts
PYTHON = $(PYBIN)/python
PIP = $(PYBIN)/pip
PYTEST = $(PYTHON) -m pytest
COVERAGE = $(PYTHON) -m coverage
PYFLAKE8 = $(PYTHON) -m flake8
TESTDIR = tests
MODULE_NAME = dupfilesremover
TMP_PATH = .\tmp

environ: clean requirements.txt requirements-dev.txt
	virtualenv $(ENV)
	$(PIP) install -r requirements-dev.txt
	@echo "initialization complete"

.PHONY: help
help:
	@echo "make                      # create virtual env and setup dependencies"
	@echo "make build_package        # build package"
	@echo "make tests                # run tests"
	@echo "make coverage             # run tests with coverage report"
	@echo "make lint                 # check linting"
	@echo "make flake8               # alias for `make lint`"
	@echo "make clean                # remove more or less everything created by make"
	@echo "make validate_package     # validates package"
	@echo "make build_package        # build package"
	@echo "make deploy               # make deploy to pypi"
	@echo "make local_install        # make local install"
	@echo "make develop_install      # make install for development"

.PHONY: tests
tests:
	$(PYTEST) $(TESTDIR) -vv

.PHONY: validate_package
validate_package: tests
	$(PYTHON) setup.py test
	$(PYTHON) setup.py check

.PHONY: build_package
build_package: tests validate_package
	$(PYTHON) setup.py sdist bdist_wheel

.PHONY: coverage
coverage:
	$(PYTEST) $(TESTDIR) -vv --cov=$(MODULE_NAME)
	$(COVERAGE) html

.PHONY: lint
lint:
	$(PYFLAKE8)
	
.PHONY: flake8
flake8:
	$(PYFLAKE8)

.PHONY: clean
clean:
	if exist $(ENV) rd $(ENV) /q /s
	if exist .coverage del .coverage
	if exist htmlcov rd htmlcov /q /s
	if exist log rd log /q /s
	if exist $(TMP_PATH) rd $(TMP_PATH) /q /s
	del /S *.pyc

.PHONY: deploy
deploy:
	$(PYTHON) setup.py sdist upload

.PHONY: local_install
local_install:
	$(PYTHON) setup.py install

.PHONY: develop_install
develop_install:
	$(PYTHON) setup.py install
	 python setup.py develop
