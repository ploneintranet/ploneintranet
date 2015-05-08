RELEASE_DIR		= release/prototype
DIAZO_DIR       = src/ploneintranet/theme/static
LATEST          = $(shell cat prototype/LATEST)
BUNDLENAME      = ploneintranet
BUNDLEURL		= https://products.syslab.com/packages/$(BUNDLENAME)/$(LATEST)/$(BUNDLENAME)-$(LATEST).tar.gz

all:: diazo
default: all
clean:
	rm bin/* .installed.cfg || true
check-clean:
	test -z "$(shell git status --porcelain)" || (git status && echo && echo "Workdir not clean." && false) && echo "Workdir clean."

########################################################################
## Setup

prototype::
	@if [ ! -d "prototype" ]; then \
		git clone https://github.com/ploneintranet/ploneintranet.prototype.git prototype; \
		cd prototype&& make; \
	 fi;

bundle:
	@cd prototype && make bundle

generate-site: prototype
	@cd prototype && make jekyll

generate-dev-site:
	@cd prototype && make dev-jekyll

copy-dev-files:
	@[ -d $(DIAZO_DIR)/generated/ ] || mkdir $(DIAZO_DIR)/generated/
	rm -rf  $(DIAZO_DIR)/generated/bundles
	cp -R prototype/_site/* $(DIAZO_DIR)/generated/

copy-files: 
	# Bundle all html, css and js into a deployable package.
	# I assume that all html in _site and js in _site/bundles is built and
	# ready for upload.
	@rm -rf ${RELEASE_DIR} && mkdir -p ${RELEASE_DIR}
	cp -R prototype/_site $(RELEASE_DIR)/
	sed -i -e "s,<script src=\"bundles/$(BUNDLENAME).js\",<script src=\"bundles/$(shell readlink prototype/bundles/$(BUNDLENAME).js)\"," $(RELEASE_DIR)/_site/*.html
	# Cleaning up non mission critical elements
	rm -f $(RELEASE_DIR)/_site/*-e
	rm -rf $(RELEASE_DIR)/_site/bundles/*
	cp prototype/bundles/$(BUNDLENAME)-$(LATEST).js $(RELEASE_DIR)/_site/bundles/
	cp prototype/bundles/$(BUNDLENAME)-$(LATEST).min.js $(RELEASE_DIR)/_site/bundles/
	ln -sf $(BUNDLENAME)-$(LATEST).js $(RELEASE_DIR)/_site/bundles/$(BUNDLENAME).js
	ln -sf $(BUNDLENAME)-$(LATEST).min.js $(RELEASE_DIR)/_site/bundles/$(BUNDLENAME).min.js
	# copy to the diazo theme dir
	@[ -d $(DIAZO_DIR)/generated/ ] || mkdir $(DIAZO_DIR)/generated/
	cp -R $(RELEASE_DIR)/_site/* $(DIAZO_DIR)/generated/

dev-diazo: bundle generate-dev-site copy-dev-files
diazo: generate-site copy-files

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
	bin/buildout -c dev.cfg

bin/buildout: bin/python2.7
	@bin/python bootstrap.py

bin/python2.7:
	@virtualenv --clear -p python2.7 .


####################################################################
# Testing

# inspect robot traceback:
# bin/robot-server ploneintranet.socialsuite.testing.PLONEINTRANET_SOCIAL_ROBOT_TESTING^
# firefox localhost:55001/plone
test-robot:
	Xvfb :99 1>/dev/null 2>&1 & HOME=/app DISPLAY=:99 bin/test -t 'robot' -x
	@ps | grep Xvfb | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

test-norobot:
	bin/test -t '!robot' -x

test: 
	Xvfb :99 1>/dev/null 2>&1 & HOME=/app DISPLAY=:99 bin/test -x
	@ps | grep Xvfb | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

.PHONY: all clean check-clean
