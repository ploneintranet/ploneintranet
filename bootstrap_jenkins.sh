#!/bin/bash
set -e
# Default to jenkins.cfg if no config file passed in
BUILDOUT_CONFIG=${1-jenkins.cfg}
PATH=/opt/src/buildout.python/python-2.7/bin:$PATH
make solr-clean clean
mkdir -p buildout-cache/downloads
rm -rf bin/ include/ lib/ local/ share/
virtualenv -p python2.7 .
. bin/activate
./bin/pip install -Ur requirements.txt
./bin/pip install -UIr requirements.txt
./bin/buildout -N -t 30 -c $BUILDOUT_CONFIG
bundle install --path vendor/bundle --binstubs
