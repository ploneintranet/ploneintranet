# This is based on the pre-commit script found at
# http://tech.yipit.com/2011/11/16/183772396/
# Using these hooks requires pep8 and jshint (for javascript)

import os
import re
import subprocess
import sys

modified = re.compile('^(?:M|A)(\s+)(?P<name>.*)')

CHECKS = [
    {
        'output': 'Checking for pdbs...',
        'command': 'grep -n "import pdb" %s',
        'ignore_files': ['.*pre-commit'],
        'print_filename': True,
    },
    {
        'output': 'Checking for ipdbs...',
        'command': 'grep -n "import ipdb" %s',
        'ignore_files': ['.*pre-commit'],
        'print_filename': True,
    },
    {
        'output': 'Running Jshint...',
        # By default, jshint prints 'Lint Free!' upon success.
        # We want to filter this out.
        'command': 'jshint %s | grep -v "Lint Free!"',
        'match_files': ['.*yipit/.*\.js$'],
        'print_filename': False,
    },
    {
        'output': 'Running flake8...',
        'command': 'bin/flake8 %s',
        'match_files': ['.*\.py$'],
        'ignore_files': ['.*migrations.*'],
        'print_filename': False,
    },
]
"""    {
    'output': 'Running Pyflakes...',
    'command': 'pyflakes %s',
    'match_files': ['.*\.py$'],
    'ignore_files': ['.*settings/.*',
        '.*manage.py',
        '.*migrations.*',
        '.*/terrain/.*'],
    'print_filename': False,
},"""


def matches_file(file_name, match_files):
    return any(re.compile(match_file).match(file_name)
               for match_file in match_files)


def check_files(files, check):
    result = 0
    print check['output']
    for file_name in files:
        if not 'match_files' in check \
                or matches_file(file_name,
                                check['match_files']):

            if not 'ignore_files' in check \
                    or not matches_file(file_name,
                                        check['ignore_files']):

# Read possible #PEP8-IGNORE to ignore the file completely
# or Pep8 options using the syntax '#PEP8 --pep8option foo'
# which would pass '--pep8option whatever' to pep8.py.
# Option must be placed in first line, first column.
                cmd = file_name
                if 'pep8' in check['output']:
                    f = open(file_name, 'r')
                    head = f.readline()
                    f.close()
                    if head[:5] == '#PEP8':
                        if head[5:12] == '-IGNORE':
                            print "Ignored file %s" % (file_name,)
                            continue
                        cmd = "%s %s" % (head[5:].strip(), file_name)
                        print "Used option '%s' for file %s" % (
                            head[5:].strip(), file_name)

                process = subprocess.Popen(check['command'] % cmd,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           shell=True)

                out, err = process.communicate()

                if out or err:
                    if check['print_filename']:
                        prefix = '\t%s:' % file_name
                    else:
                        prefix = '\t'

                    output_lines = [
                        '%s%s' % (prefix, line) for line in out.splitlines()]
                    print '\n'.join(output_lines)
                    if err:
                        print err
                    result = 1
    return result


def main(all_files):
    # Stash any changes to the working tree that are not going to be committed
    subprocess.call(['git',
                     'stash',
                     '--keep-index'],
                    stdout=subprocess.PIPE)

    files = []
    if all_files:
        for root, dirs, file_names in os.walk('.'):
            for file_name in file_names:
                files.append(os.path.join(root, file_name))
    else:
        p = subprocess.Popen(['git', 'status', '--porcelain'],
                             stdout=subprocess.PIPE)
        out, err = p.communicate()
        for line in out.splitlines():
            match = modified.match(line)
            if match:
                files.append(match.group('name'))

    result = 0

    #return_code = subprocess.call('/usr/bin/python manage.py validate',
    #    shell=True)
    #result = return_code or result

    for check in CHECKS:
        result = check_files(files, check) or result

    # Unstash changes to the working tree that we had stashed
    subprocess.call(['git', 'stash', 'pop', '-q'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.exit(result)


if __name__ == '__main__':
    all_files = False
    if len(sys.argv) > 1 and sys.argv[1] == '--all-files':
        all_files = True
    main(all_files)
