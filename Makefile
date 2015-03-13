BOWER 		?= node_modules/.bin/bower
JSHINT 		?= node_modules/.bin/jshint
PEGJS		?= node_modules/.bin/pegjs
PHANTOMJS	?= node_modules/.bin/phantomjs

PATTERNS	= src/bower_components/patternslib
SOURCES		= $(wildcard $(PATTERNS)/src/*.js) $(wildcard $(PATTERNS)/src/pat/*.js) $(wildcard $(PATTERNS)/src/lib/*.js)
BUNDLES		= bundles/patterns.js bundles/patterns.min.js

GENERATED	= $(PATTERNS)/src/lib/depends_parse.js

JSHINTEXCEPTIONS = $(GENERATED) \
		   $(PATTERNS)/src/lib/dependshandler.js \
		   $(PATTERNS)/src/lib/htmlparser.js \
		   $(PATTERNS)/src/pat/skeleton.js
CHECKSOURCES	= $(filter-out $(JSHINTEXCEPTIONS),$(SOURCES))

RELEASE         = $(shell git describe --tags)
RELEASE_DIR		= release/prototype
RELEASE_TARBALL = release/prototype-$(RELEASE).tar.gz

DIAZO_DIR   = src/ploneintranet/theme/static

LATEST          = $(shell cat LATEST)
BUNDLENAME      = ploneintranet
BUNDLEURL		= https://products.syslab.com/packages/$(BUNDLENAME)/$(LATEST)/$(BUNDLENAME)-$(LATEST).tar.gz


all:: bundle.js diazo
default: all

########################################################################
## Install dependencies

stamp-npm: package.json
	npm install
	touch stamp-npm

stamp-bower: stamp-npm
	$(BOWER) install
	touch stamp-bower


#patterns:
#	if test -d src/Patterns; then cd src/Patterns && git pull && cd ../..; else git clone https://github.com/Patternslib/Patterns.git src/Patterns; fi

clean-stamps::
	rm -f stamp-npm stamp-bower

clean:: clean-stamps clean-buildout
	rm -rf node_modules src/bower_components ~/.cache/bower

clean-buildout:
	rm bin/* .installed.cfg || true


########################################################################
## Tests

check:: jshint test-bundle
jshint: stamp-npm
	$(JSHINT) --config jshintrc $(CHECKSOURCES) build.js


check:: stamp-npm
	$(PHANTOMJS) node_modules/phantom-jasmine/lib/run_jasmine_test.coffee tests/TestRunner.html


########################################################################
## Bundle generation

bundle bundle.js: stamp-bower $(GENERATED) $(SOURCES) build.js jekyll
	node_modules/.bin/r.js -o build.js optimize=none
	node_modules/.bin/grunt uglify
	mkdir -p prototype/bundles
	mv bundle.js prototype/bundles/$(BUNDLENAME)-$(RELEASE).js
	ln -sf $(BUNDLENAME)-$(RELEASE).js prototype/bundles/$(BUNDLENAME).js
	mkdir -p prototype/_site/bundles
	cp prototype/bundles/$(BUNDLENAME)-$(RELEASE).js prototype/_site/bundles/$(BUNDLENAME).js
	mv bundle.min.js prototype/bundles/$(BUNDLENAME)-$(RELEASE).min.js
	ln -sf $(BUNDLENAME)-$(RELEASE).min.js prototype/bundles/$(BUNDLENAME).min.js
	cp prototype/bundles/$(BUNDLENAME)-$(RELEASE).min.js prototype/_site/bundles/$(BUNDLENAME).min.js

test-bundle test-bundle.js: stamp-bower $(GENERATED) $(SOURCES) test-build.js
	node_modules/.bin/r.js -o test-build.js


$(PATTERNS)/src/lib/depends_parse.js: $(PATTERNS)/src/lib/depends_parse.pegjs stamp-npm
	$(PEGJS) $<
	sed -i~ -e '1s/.*/define(function() {/' -e '$$s/()//' $@ || rm -f $@

check-clean:
	test -z "$(shell git status --porcelain)" || (git status && echo && echo "Workdir not clean." && false) && echo "Workdir clean."

jsrelease: bundle.js
	# This one is used by developers only and can be used separately to do a
	# version for Designers only
	mkdir -p release
	cp prototype/bundles/$(BUNDLENAME)-$(RELEASE).js release
	tar cfz release/$(BUNDLENAME)-$(RELEASE).js.tar.gz -C release $(BUNDLENAME)-$(RELEASE).js
	curl -X POST -F 'content=@release/$(BUNDLENAME)-$(RELEASE).js.tar.gz' 'https://products.syslab.com/?name=$(BUNDLENAME)&version=$(RELEASE)&:action=file_upload'
	rm release/$(BUNDLENAME)-$(RELEASE).js.tar.gz
	echo "Upload done."
	echo "$(RELEASE)" > LATEST
	git add LATEST
	git commit -m "distupload: updated latest file to recent js bundle"
	git push

designerhappy:
	mkdir -p prototype/bundles
	curl $(BUNDLEURL) -o prototype/bundles/$(BUNDLENAME)-$(LATEST).tar.gz
	cd prototype/bundles && tar xfz $(BUNDLENAME)-$(LATEST).tar.gz && rm $(BUNDLENAME)-$(LATEST).tar.gz
	cd prototype/bundles && if test -e $(BUNDLENAME).js; then rm $(BUNDLENAME).js; fi
	cd prototype/bundles && ln -sf $(BUNDLENAME)-$(LATEST).js $(BUNDLENAME).js
	echo "The latest js bundle has been downloaded to prototype/bundles. You might want to run jekyll. Designer, you can be happy now."


gems:
	cd prototype && mkdir -p .bundle/gemfiles && bundle install --path .bundle/gemfiles

jekyll: gems
	cd prototype && bundle exec jekyll build

dev: jekyll
	# Set up development environment
	# install a require.js config
	cp src/bower_components/requirejs/require.js prototype/_site/bundles/$(BUNDLENAME)-modular.js
	ln -s ../../../src prototype/_site/bundles
	ln -s src/patterns.js prototype/_site/main.js

diazo release: jekyll bundle.js
	# Bundle all html, css and js into a deployable package.
	# I assume that all html in _site and js in _site/bundles is built and
	# ready for upload.
	# CAVE: This is currently work in progress and was used to deploy to deliverance
	# We will most probably rewrite this to deploy all necessary resources
	# for diazo into egg format (Yet to be decided how)
	#
	@[ -d release/prototype ] || mkdir -p release/prototype
	# make sure it is empty
	rm -rf release/prototype/*
	# test "$$(git status --porcelain)x" = "x" || (git status && false)
	cp -R prototype/_site $(RELEASE_DIR)/
	sed -i -e "s,<script src=\"bundles/$(BUNDLENAME).js\",<script src=\"bundles/$(shell readlink prototype/bundles/$(BUNDLENAME).js)\"," $(RELEASE_DIR)/_site/*.html
	# Cleaning up non mission critical elements
	rm -f $(RELEASE_DIR)/_site/*-e
	rm -rf $(RELEASE_DIR)/_site/bundles/*
	cp prototype/bundles/$(BUNDLENAME)-$(RELEASE).js $(RELEASE_DIR)/_site/bundles/
	cp prototype/bundles/$(BUNDLENAME)-$(RELEASE).min.js $(RELEASE_DIR)/_site/bundles/
	ln -sf $(BUNDLENAME)-$(RELEASE).js $(RELEASE_DIR)/_site/bundles/$(BUNDLENAME).js
	ln -sf $(BUNDLENAME)-$(RELEASE).min.js $(RELEASE_DIR)/_site/bundles/$(BUNDLENAME).min.js
	# replace absolute resource urls with relative
	sed -i -e "s#http://patterns.cornae.com/#./#" $(RELEASE_DIR)/_site/*.html
	# copy to the diazo theme dir
	@[ -d $(DIAZO_DIR)/generated/ ] || mkdir $(DIAZO_DIR)/generated/
	cp -R $(RELEASE_DIR)/_site/* $(DIAZO_DIR)/generated/

clean::
	rm -f bundle.js
	rm -rf prototype/bundles/*


.PHONY: all bundle clean check jshint tests check-clean release

####################################################################
# docker.io

PROJECT=ploneintranet

docker-build: .ssh/known_hosts
	docker build -t $(PROJECT) .

# re-uses ssh agent
# also loads your standard .bashrc
docker-run:
	docker run -i -t \
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

# for development
demo-run:
	cd prototype &&	bundle exec jekyll serve --watch --baseurl ""

# for demo.ploneintranet.net deployment
demo-build:
	cd prototype &&	bundle exec jekyll build


.ssh/known_hosts:
	mkdir -p .ssh
	echo "|1|YftEEH4HWPOfSNPY/5DKE9sxj4Q=|UDelHrh+qov24v5GlRh2YCCWcRM= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==" > .ssh/known_hosts


# Guido's lazy targets



devel: bin/buildout
	bin/buildout -c dev.cfg

bin/buildout: bin/python2.7
	@bin/python bootstrap.py

bin/python2.7:
	@virtualenv --clear -p python2.7 .


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
