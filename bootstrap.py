from subprocess import CalledProcessError
from subprocess import check_call

import os
import sys


python_path = sys.executable
bin_dir = os.path.dirname(python_path)
pip_path = os.path.join(bin_dir, "pip")
command = "{0} install -r requirements.txt".format(pip_path)


try:
    print "Running bootstrap: {0}".format(command)
    check_call(command.split(" "))
    print "Bootstrap complete"
except CalledProcessError:
    print "Please try to bootstrap manually using: {0}".format(command)


