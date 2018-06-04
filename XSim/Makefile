SRCS = __init__.py
SRCS += XSimBench.py
SRCS += XSimParam.py
SRCS += XSimStimulus.py
SRCS += XSimResult.py

PYTHON_VERSION = python3.6
PYTHON_DIR = /home/gwb/miniconda3

all: install

$(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/xsim:
	mkdir -p $(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/xsim

install: $(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/xsim
	cp $(SRCS) $(PYTHON_DIR)/lib/$(PYTHON_VERSION)/site-packages/xsim
