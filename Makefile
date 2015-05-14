RELEASE_DIR	= release/prototype/_site
DIAZO_DIR       = src/ploneintranet/theme/static/generated
LATEST          = $(shell cat LATEST)
BUNDLENAME      = ploneintranet
BUNDLEURL	= https://products.syslab.com/packages/$(BUNDLENAME)/$(LATEST)/$(BUNDLENAME)-$(LATEST).tar.gz

# Add help text after each target name starting with ' \#\# '
help:
	@grep " ## " $(MAKEFILE_LIST) | grep -v MAKEFILE_LIST | sed 's/\([^:]*\).*##/\1\t/'

all:: fetchrelease
default: all
clean:
	rm bin/* .installed.cfg || true
check-clean:
	test -z "$(shell git status --porcelain)" || (git status && echo && echo "Workdir not clean." && false) && echo "Workdir clean."

fetchrelease: ## Download and install the latest javascript bundle into the theme.
	$(eval LATEST := $(shell cat LATEST))
	$(eval BUNDLEURL := https://products.syslab.com/packages/$(BUNDLENAME)/$(LATEST)/$(BUNDLENAME)-$(LATEST).tar.gz)
	# fetch non-git-controlled required javascript resources
	@[ -d $(DIAZO_DIR)/bundles/ ] || mkdir -p $(DIAZO_DIR)/bundles/
	@curl $(BUNDLEURL) -o $(DIAZO_DIR)/bundles/$(BUNDLENAME)-$(LATEST).tar.gz
	@cd $(DIAZO_DIR)/bundles/ && tar xfz $(BUNDLENAME)-$(LATEST).tar.gz && rm $(BUNDLENAME)-$(LATEST).tar.gz
	@cd $(DIAZO_DIR)/bundles/ && if test -e $(BUNDLENAME).js; then rm $(BUNDLENAME).js; fi
	@cd $(DIAZO_DIR)/bundles/ && if test -e $(BUNDLENAME).min.js; then rm $(BUNDLENAME).min.js; fi
	@cd $(DIAZO_DIR)/bundles/ && ln -sf $(BUNDLENAME)-$(LATEST).js $(BUNDLENAME).js
	@cd $(DIAZO_DIR)/bundles/ && ln -sf $(BUNDLENAME)-$(LATEST).min.js $(BUNDLENAME).min.js

########################################################################
## Setup
## You don't run these rules unless you're a prototype dev

prototype:: ## Get the latest version of the prototype
	@if [ ! -d "prototype" ]; then \
		git clone https://github.com/ploneintranet/ploneintranet.prototype.git prototype; \
	else \
		cd prototype && git pull; \
	fi;
	cp prototype/LATEST .

jekyll: prototype
	@cd prototype && make jekyll

diazorelease: diazo ## Run 'diazo' and commit all changes to the generated theme, including removals
	git add --all $(DIAZO_DIR)
	@echo "=========================="
	@git status
	@echo "=========================="
	@echo 'Ready to do: git commit -a -m "protoype release $(shell cat LATEST)"'
	@echo "^C to abort (10 sec)"
	@sleep 10
	git commit -a -m "protoype release $(shell cat LATEST)"

diazo: jekyll fetchrelease _diazo ## Generate the theme with jekyll and copy it to src/ploneintranet/theme/static/generated
_diazo:
	# --- (1) --- prepare clean release dir
	@rm -rf ${RELEASE_DIR} && mkdir -p ${RELEASE_DIR}
	cp -R prototype/_site/* $(RELEASE_DIR)/
	# Cleaning up non mission critical elements
	rm -f $(RELEASE_DIR)/*-e
	rm -rf $(RELEASE_DIR)/bundles/*
	# --- (2) --- refresh diazo static/generated
	# html templates referenced in rules.xml - second cut preserves subpath eg open-market-committee/index.html
	# point js sourcing to registered resource and rewrite all other generated sources to point to diazo dir
	for file in `grep generated $(DIAZO_DIR)/../rules.xml | cut -f2 -d\" | cut -f2- -d/`; do \
		sed -i -e 's#src=".*ploneintranet.js"#src="++theme++ploneintranet.theme/generated/bundles/$(BUNDLENAME).js"#' $(RELEASE_DIR)/$$file; \
		sed -i -e 's#http://demo.ploneintranet.net/#++theme++ploneintranet.theme/generated/#g' $(RELEASE_DIR)/$$file; \
		mkdir -p `dirname $(DIAZO_DIR)/$$file`; \
		cp $(RELEASE_DIR)/$$file $(DIAZO_DIR)/$$file; \
	done
	# we want all style elements recursively - and remove old resources not used anymore
	@rm -rf $(DIAZO_DIR)/style/ && mkdir $(DIAZO_DIR)/style/
	cp -R $(RELEASE_DIR)/style/* $(DIAZO_DIR)/style/
	# logo
	@[ -d $(DIAZO_DIR)/media/ ] || mkdir $(DIAZO_DIR)/media/
	cp $(RELEASE_DIR)/media/logo*.svg $(DIAZO_DIR)/media/

jsdev: dev-bundle diazo _jsdev ## full js development refresh

# fast replace ploneintranet-dev.js - requires diazo to have run!
_jsdev:
	# replace normal js bundle with dev bundle, directly in diazo theme dir
	cp prototype/bundles/$(BUNDLENAME)-dev.js $(DIAZO_DIR)/bundles/ploneintranet.js

dev-bundle: prototype
	cd prototype && make dev-bundle

bundle: prototype
	cd prototype && make bundle

jsrelease: prototype
	cd prototype && make jsrelease
	cp prototype/LATEST .


####################################################################
# docker.io

PROJECT=ploneintranet

docker-build: .ssh/known_hosts
	docker.io build -t $(PROJECT) .

# re-uses ssh agent
# also loads your standard .bashrc
docker-run:
	docker.io run -i -t \
                --net=host \
                -v $(SSH_AUTH_SOCK):/tmp/auth.sock \
                -v $(HOME)/.buildout:/.buildout \
                -v /var/tmp:/var/tmp \
                -v $(HOME)/.bashrc:/.bashrc \
                -v $(HOME)/.gitconfig:/.gitconfig \
                -v $(HOME)/.gitignore:/.gitignore \
                -e SSH_AUTH_SOCK=/tmp/auth.sock \
		-e LC_ALL=en_US.UTF-8 \
		-e LANG=en_US.UTF-8 \
                -v $(PWD):/app -w /app -u app $(PROJECT)

.ssh/known_hosts:
	mkdir -p .ssh
	echo "|1|YftEEH4HWPOfSNPY/5DKE9sxj4Q=|UDelHrh+qov24v5GlRh2YCCWcRM= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==" > .ssh/known_hosts

####################################################################
# Guido's lazy targets

devel: bin/buildout
	bin/buildout

bin/buildout: bin/python2.7
	@bin/python bootstrap.py

bin/python2.7:
	@virtualenv --clear -p python2.7 .


####################################################################
# Testing

# inspect robot traceback:
# bin/robot-server ploneintranet.suite.testing.PLONEINTRANET_SUITE_ROBOT
# firefox localhost:55001/plone
test-robot: ## Run robot tests with a virtual X server
	Xvfb :99 1>/dev/null 2>&1 & HOME=/app DISPLAY=:99 bin/test -t 'robot' -x
	@ps | grep Xvfb | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

test-norobot: ## Run all tests apart from robot tests
	bin/test -t '!robot' -x

test: ## Run all tests, including robot tests with a virtual X server
	Xvfb :99 1>/dev/null 2>&1 & HOME=/app DISPLAY=:99 bin/test -x
	@ps | grep Xvfb | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

.PHONY: all clean check-clean
