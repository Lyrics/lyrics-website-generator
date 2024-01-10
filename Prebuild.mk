#!/usr/bin/make -f

INSTALL_DEPENDENCIES: ## Install required dependencies
	@PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install --user -r requirements.txt
.PHONY: INSTALL_DEPENDENCIES
