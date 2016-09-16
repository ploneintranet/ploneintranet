default: help

# Add help text after each target name starting with ' \#\# '
help:
	@grep " ## " $(MAKEFILE_LIST) | grep -v MAKEFILE_LIST | sed 's/\([^:]*\).*##/\1\t/'


devel: bin/buildout ldap/schema ## 	 Run development buildout
	bin/buildout

ldap/schema:
	[ -L ldap/schema ] || ln -s /etc/ldap/schema ldap/schema

clean:
	rm bin/* .installed.cfg || true
clean-proto:
	cd prototype && make clean
check-clean:
	test -z "$(shell git status --porcelain)" || (git status && echo && echo "Workdir not clean." && false) && echo "Workdir clean."

fetchrelease: deprecated

########################################################################
## Setup
## You don't run these rules unless you're a prototype dev

deprecated:
	@echo "Theme development is now done in quaive.resources.ploneintranet"

prototype: ## Get the latest version of the prototype
	@if [ ! -d "prototype" ]; then \
		git clone git@github.com:quaive/ploneintranet.prototype.git prototype; \
	else \
		cd prototype && git pull; \
	fi;

latest: deprecated

jekyll: prototype
	@echo 'DO: rm prototype/stamp-bundler to force Jekyll re-install'
	@cd prototype && make jekyll

diazorelease: deprecated
diazo: deprecated

jsdev: deprecated

dev-bundle: prototype
	cd prototype && make dev-bundle

bundle: prototype
	cd prototype && make bundle

jsrelease: deprecated

demo: jekyll demo-run

demo-run:
	cd prototype && make demo-run

# demo buildout with CSRF disabled
demo-buildout: bin/buildout
	bin/buildout -c demo.cfg

####################################################################
# docker.io
# see comments for using boot2docker on MacOSX

PROJECT=quaive/ploneintranet-dev

docker-build: .ssh/known_hosts  ## Create docker container
	docker build -t $(PROJECT) .

# re-uses ssh agent
# also loads your standard .bashrc
docker-run:  ## Start docker container
	docker run -i -t \
                --net=host \
                -v /var/tmp:/var/tmp \
                -v $(SSH_AUTH_SOCK):/tmp/auth.sock \
                -v $(HOME)/.bashrc:/app/.bashrc \
                -v $(HOME)/.buildout:/app/.buildout \
                -v $(HOME)/.pypirc:/app/.pypirc \
                -v $(HOME)/.gitconfig:/app/.gitconfig \
                -v $(HOME)/.gitignore_global:/app/.gitignore_global \
                -e SSH_AUTH_SOCK=/tmp/auth.sock \
		-e PYTHON_EGG_CACHE=/var/tmp/python-eggs \
		-e LC_ALL=en_US.UTF-8 \
		-e LANG=en_US.UTF-8 \
                -v $(PWD):/app -w /app -u app $(PROJECT)

.ssh/known_hosts:
	mkdir -p .ssh
	echo "|1|YftEEH4HWPOfSNPY/5DKE9sxj4Q=|UDelHrh+qov24v5GlRh2YCCWcRM= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==" > .ssh/known_hosts

####################################################################
# Guido's lazy targets

gitlab-ci: bin/buildout
	bin/buildout -c gitlab-ci.cfg

bin/buildout: bin/python2.7
	@bin/pip install -UIr requirements.txt

bin/python2.7:
	@virtualenv --clear -p python2.7 .

devrun:
	sudo service redis-server start
	bin/supervisord
	bin/supervisorctl stop instance instance2
	bin/instance fg

####################################################################
# Solr

solr: devel

solr-clean:
	rm -rf parts/solr parts/solr-test var/solr var/solr-test bin/solr-instance bin/solr-test

all-clean: db-clean solr-clean clean

db-clean:
	bin/supervisorctl shutdown || true
	@echo "This will destroy your local database! ^C to abort..."
	@sleep 10
	rm -rf var/filestorage var/blobstorage

allclean: all-clean

####################################################################
# Testing

test-docsplit:  ## Verify that docsplit dependencies are installed
	@docsplit images -o /tmp testfiles/plone.pdf
	@docsplit images -o /tmp testfiles/minutes.docx
	@echo "Docsplit seems to be installed OK, no errors."

# inspect robot traceback:
# bin/robot-server ploneintranet.suite.testing.PLONEINTRANET_SUITE_ROBOT
# firefox localhost:55001/plone
# To see the tests going on, use DISPLAY=:0, or use Xephyr -screen 1024x768 instead of Xvfb
# ROBOT_SELENIUM_RUN_ON_FAILURE=Debug DISPLAY=:0 bin/test -s ploneintranet.suite -t post_file.robot
test-robot: ## Run robot tests with a virtual X server
	Xvfb :99 1>/dev/null 2>&1 & DISPLAY=:99 bin/test -t 'robot'
	@ps | grep Xvfb | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

test-norobot: ## Run all tests apart from robot tests
	bin/test -t '!robot'

test:: ## 	 Run all tests, including robot tests with a virtual X server
	Xvfb :99 1>/dev/null 2>&1 & DISPLAY=:99 bin/test
	@ps | grep Xvfb | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

####################################################################
# Documentation
docs:
	@bin/sphinx-build -b html -d docs/doctrees -D latex_paper_size=a4 docs docs/html

# Re-generate
api-docs:
	@bin/sphinx-apidoc -P -o docs/api src/ploneintranet

docs-clean:
	rm -rf docs/html

.PHONY: all docs api-docs docs-clean clean check-clean solr-clean
