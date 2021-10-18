all: venv install

venv:
	python -m venv venv && source venv

install:
	pip install -r requirements.txt
