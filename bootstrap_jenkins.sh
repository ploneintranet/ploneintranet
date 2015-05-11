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
./bin/python bootstrap.py || exit 1
virtualenv --relocatable .
./bin/buildout -N -t 10 -c jenkins.cfg || exit 1
virtualenv --relocatable .
bundle install --path vendor/bundle --binstubs
./bin/develop up -f || exit 1

