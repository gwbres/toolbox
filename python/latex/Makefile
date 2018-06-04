SRCS = latex.py

PYTHON_VERSION = python3.6
PYTHON_DIR = /home/gwb/miniconda3

all: install

$(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/latex:
	mkdir -p $(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/latex

install: $(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/latex
	cp $(SRCS) $(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/latex
	cp latex-include.py $(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/latex.py
	cp latex-include.py $(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/latex/__init__.py
