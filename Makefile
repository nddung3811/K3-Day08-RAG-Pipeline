SHELL := /bin/bash

PYTHON ?= .venv/bin/python
PIP := $(PYTHON) -m pip
STREAMLIT := $(PYTHON) -m streamlit

.PHONY: help install install-full run test compile

help:
	@echo "Available commands:"
	@echo "  make install   Install dependencies needed to run the UI"
	@echo "  make install-full  Install the complete RAG/evaluation stack"
	@echo "  make run       Start the Streamlit app"
	@echo "  make test      Run tests"
	@echo "  make compile   Check Python syntax"

install:
	$(PIP) install "streamlit>=1.35.0" "python-dotenv>=1.0.0"

install-full:
	$(PIP) install --prefer-binary -r requirements.txt

run:
	@if [ ! -x "$(PYTHON)" ]; then \
		echo "Python environment not found: $(PYTHON)"; \
		echo "Create it with: python3 -m venv .venv"; \
		exit 1; \
	fi
	$(STREAMLIT) run app.py

test:
	$(PYTHON) -m pytest

compile:
	$(PYTHON) -m py_compile app.py src/*.py tests/*.py
