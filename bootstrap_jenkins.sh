virtualenv --no-setuptools .
mkdir -p buildout-cache/downloads
./bin/python bootstrap.py -v 1.6.3
./bin/buildout -c travis.cfg buildout:develop= install download install
./bin/buildout -N -t 3 -c travis.cfg
Xvfb :99 -a &
