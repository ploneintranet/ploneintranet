if [ ! -f bin/activate ] 
then
    virtualenv  .
fi
mkdir -p buildout-cache/downloads || exit 1
./bin/python bootstrap.py || exit 1
./bin/buildout -N -t 3 -c jenkins.cfg || exit 1
bundle install --path vendor/bundle --binstubs
./bin/develop up -f || exit 1
make clean-stamps all || exit 1
