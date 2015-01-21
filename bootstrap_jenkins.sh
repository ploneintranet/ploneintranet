virtualenv --no-setuptools .
mkdir -p buildout-cache/downloads || exit 1
./bin/python bootstrap.py || exit 1
./bin/buildout -c travis.cfg buildout:develop= install download install || exit 1
./bin/buildout -N -t 3 -c jenkins.cfg || exit 1
./bin/develop up -f || exit 1
cd src/ploneintranet.theme && make diazo || exit 1
