#!/usr/bin/make -f

INSTALL_DEPENDENCIES: ## Install required dependencies
	@pip3 install --user -r requirements.txt
.PHONY: INSTALL_DEPENDENCIES
