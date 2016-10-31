# Default to jenkins.cfg if no config file passed in
BUILDOUT_CONFIG=${1-jenkins.cfg}
make solr-clean clean
if [ ! -f bin/activate ]
then
    virtualenv .
fi
mkdir -p buildout-cache/downloads || exit 1

# NOTE: we need to use virtualenv --relocatable every time new
# console_scripts have been created in ./bin to avoid running into the
# problem where the shebang is > 127 characters long.

virtualenv --relocatable .
. bin/activate
rm -rf local/lib/python2.7/site-packages/easy_install* local/lib/python2.7/site-packages/setuptools* 2>/dev/null || true
./bin/pip install -UIr requirements.txt || exit 1
virtualenv --no-setuptools --relocatable .
./bin/buildout -N -t 10 -c $BUILDOUT_CONFIG || exit 1
virtualenv --no-setuptools --relocatable .
bundle install --path vendor/bundle --binstubs
./bin/develop up -f || exit 1
