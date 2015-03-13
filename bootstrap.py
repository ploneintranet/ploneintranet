from subprocess import CalledProcessError
from subprocess import check_call

import os
import shlex
import sys


python_path = sys.executable
bin_dir = os.path.dirname(python_path)
pip_path = os.path.join(bin_dir, "pip")
out_path = "{0}/bin".format(os.getcwd())
bootstrap_clean = "{0} uninstall -y zc.buildout".format(pip_path)
bootstrap = (
    '{0} install -r requirements.txt --install-option="--install-scripts={1}"'
).format(pip_path, out_path)

if not os.path.exists(pip_path):
    print ("pip is not installed in your virtualenv. Reinstall your "
           "virtualenv without using the --no-setuptools or --no-pip options.")
    sys.exit(1)
try:
    print "Cleaning up from previous bootstrap: {0}".format(bootstrap_clean)
    check_call(bootstrap_clean.split(" "))
except CalledProcessError:
    print "Ready for bootstrap"
try:
    print "Running bootstrap command: {0}".format(bootstrap)
    check_call(shlex.split(bootstrap))
    print "Bootstrap complete"
except CalledProcessError:
    print "Please try to bootstrap manually using: {0}".format(bootstrap)
