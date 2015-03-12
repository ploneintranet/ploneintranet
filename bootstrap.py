from subprocess import CalledProcessError
from subprocess import check_call

import os
import sys


python_path = sys.executable
bin_dir = os.path.dirname(python_path)
pip_path = os.path.join(bin_dir, "pip")
bootstrap_clean = "{0} uninstall -y zc.buildout".format(pip_path)
bootstrap = "{0} install -r requirements.txt".format(pip_path)

try:
    print "Cleaning up from previous bootstrap: {0}".format(bootstrap_clean)
    check_call(bootstrap_clean.split(" "))
except CalledProcessError:
    print "Ready for bootstrap"
try:
    print "Running bootstrap command: {0}".format(bootstrap)
    check_call(bootstrap.split(" "))
    print "Bootstrap complete"
except CalledProcessError:
    print "Please try to bootstrap manually using: {0}".format(bootstrap)
