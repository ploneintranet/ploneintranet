import argparse
import git
import os
import re
import subprocess

buildout_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..', '..'))


class RunAllTestsException(Exception):
    """Raised to indicate that all tests should be run"""


class Strategy(object):

    wildcard = False  # if True executes full test suite on trigger match
    triggers = {}
    packages = {}
    tests = {}

    def __init__(self, name):
        self.name = name

    def __call__(self, whatchanged, verbose=True):
        for trigger in self.triggers:
            matcher = re.compile(trigger)
            for path in whatchanged:
                if matcher.match(path):
                    if verbose:
                        marker = self.wildcard and "* " or "- "
                        print("{}{} matched on {}".format(
                            marker, self.name, path))
                    if self.wildcard:
                        raise RunAllTestsException(path)
                    return (set(self.packages), set(self.tests))
        return ({}, {})


class Policy(object):

    def __init__(self, *strategies):
        self.strategies = list(strategies)

    def add(self, strategy):
        self.strategies.append(strategy)

    def __call__(self, whatchanged, verbose=True):
        packages = set()
        tests = set()
        for strategy in self.strategies:
            try:
                (_packages, _tests) = strategy(whatchanged, verbose)
            except RunAllTestsException:
                return ({}, {})
            packages = packages.union(_packages)
            tests = tests.union(_tests)
        return (packages, tests)


def spec(operator, selectors):
    return ' '.join("{} {}".format(operator, item) for item in selectors)


def main():
    parser = argparse.ArgumentParser("Fastest - Fast diff test runner")
    parser.add_argument("--from",
                        help="Git ref to test (default: HEAD)")
    parser.add_argument("--to",
                        help="Git ref to diff against (default: master)")
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help="do everything except actually executing tests")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='suppress output')
    args = parser.parse_args()
    verbose = not args.quiet
    _from = getattr(args, 'from') or 'HEAD'
    _to = getattr(args, 'to') or 'master'
    dryrun = args.dry_run
    if verbose:
        print ("Testing changes from {} to {}".format(
            _from, _to))
    changes = whatchanged(_from, _to)
    from .config import POLICY
    (packages, tests) = POLICY(changes, verbose=verbose)
    spec_pkg = spec('-s', packages)
    spec_tst = spec('-t', tests)
    if packages and tests:
        run_multi(spec_pkg, spec_tst, verbose=verbose, dryrun=dryrun)
    elif packages:
        run(spec_pkg, verbose=verbose, dryrun=dryrun)
    elif tests:
        run(spec_tst, verbose=verbose, dryrun=dryrun)
    else:
        run('', verbose=verbose, dryrun=dryrun)


def repo():
    """In case of a non-git (egg) release tests will be disabled"""
    return git.Repo(buildout_dir)


def whatchanged(commitid, sinceid=None):
    if not sinceid:
        sinceid = '{}^'.format(commitid)
    commit = repo().commit(commitid)
    since = repo().commit(sinceid)
    return {x.a_path or x.b_path for x in commit.diff(since)}


def run(testspec, verbose=True, dryrun=False):
    testrunner = os.path.join(buildout_dir, 'bin', 'test')
    command = '{} {}'.format(testrunner, testspec)
    if verbose:
        print("Firing subprocess: {}".format(command))
    else:
        command += " >/dev/null"
    if not dryrun:
        return subprocess.call(command, shell=True)


def run_multi(speclist, verbose=True, dryrun=False):
    status = 0
    for testspec in speclist:
        status += run(testspec, verbose, dryrun)
    return status
