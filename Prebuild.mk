#!/usr/bin/make -f

INSTALL_DEPENDENCIES: ## Install required dependencies
	@pip3 install --user -r requirements.txt --break-system-packages
.PHONY: INSTALL_DEPENDENCIES
