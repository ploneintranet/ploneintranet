virtualenv --no-setuptools .
mkdir -p buildout-cache/downloads
./bin/python bootstrap.py
./bin/buildout -c travis.cfg buildout:develop= install download install
./bin/buildout -N -t 3 -c jenkins.cfg
./bin/develop up -f
# Xvfb :99 -a &
