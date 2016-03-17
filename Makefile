# Some simple testing tasks (sorry, UNIX only).

PYTHON=venv/bin/python
PIP=venv/bin/pip
FLAGS=


update:
	$(PYTHON) ./setup.py install

install:
	python3 -m venv venv
	$(PYTHON) ./setup.py install

venv:
	python3 -m venv venv
	$(PIP) install -r requirements.txt
	$(PYTHON) ./setup.py develop
