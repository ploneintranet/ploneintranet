import ConfigParser
import argparse
import git
import os
import re
import subprocess

repo_dir = os.path.abspath(os.path.join(__file__, '..', '..', '..', '..'))


class RunAllTestsException(Exception):
    """Raised to indicate that ALL tests should be run"""


class RunNoTestsException(Exception):
    """Raised to indicate that NO tests should be run"""


class Strategy(object):

    wildcard = False  # if True executes full test suite on trigger match
    triggers = set()
    packages = set()
    tests = set()

    def __init__(self, name):
        self.name = name

    def __call__(self, whatchanged, verbose=True):
        for trigger in self.triggers:
            matcher = re.compile(trigger)
            for path in whatchanged:
                if matcher.search(path):
                    if verbose:
                        marker = self.wildcard and "* " or "- "
                        print("{}[{:_^12}] triggered by {}".format(
                            marker, self.name, path))
                    if self.wildcard:
                        raise RunAllTestsException(path)
                    return (set(self.packages), set(self.tests))
        return (set(), set())

    def match(self, changeset):
        matchers = [re.compile(trigger) for trigger in self.triggers]
        matching = set()
        for path in changeset:
            for matcher in matchers:
                if matcher.match(path):
                    matching.add(path)
        return matching

    def __repr__(self):
        return "<Strategy:{}>".format(self.name)


class Policy(object):

    strategies = []

    def __init__(self, configpath=None):
        if configpath:
            self.read_config(configpath)

    def add(self, *strategies):
        self.strategies.extend(strategies)

    def read_config(self, filepath):
        config = ConfigParser.ConfigParser()
        config.read(filepath)
        if 'policy' not in config.sections():
            raise ValueError("Required [policy] section missing in {}".format(
                filepath))

        def safe_get(config, sectionid, varname):
            try:
                return config.get(sectionid, varname).strip().split()
            except ConfigParser.NoOptionError:
                return []

        for id in safe_get(config, 'policy', 'strategies'):
            strategy = Strategy(id)
            strategy.triggers = safe_get(config, id, 'triggers')
            strategy.packages = safe_get(config, id, 'packages')
            strategy.tests = safe_get(config, id, 'tests')
            try:
                strategy.wildcard = config.getboolean(id, 'wildcard')
            except ConfigParser.NoOptionError:
                pass  # defaults to False anyway
            self.add(strategy)

    def __call__(self, whatchanged, verbose=True):
        matching = set()
        for strategy in self.strategies:
            matching = matching.union(strategy.match(whatchanged))
        if matching != whatchanged:
            if verbose:
                print("Changes detected outside of optimization strategies:")
                for path in (whatchanged - matching):
                    print("  {}".format(path))
                print("Running all tests.")
            return (set(), set())
        # only if each path had a match do we dare to optimize
        else:
            return self.optimized(whatchanged, verbose)

    def optimized(self, whatchanged, verbose=True):
        packages = set()
        tests = set()
        for strategy in self.strategies:
            try:
                (_packages, _tests) = strategy(whatchanged, verbose)
            except RunAllTestsException:
                return (set(), set())
            packages = packages.union(_packages)
            tests = tests.union(_tests)
        return (packages, tests)


def spec(operator, selectors):
    return ' '.join("{} {}".format(operator, item) for item in selectors)


def main():
    configpath = os.path.join(os.path.dirname(__file__), 'policy.cfg')
    epilog = "You should schedule two separate runs: --run 1 and --run 2"
    parser = argparse.ArgumentParser("fastest",
                                     epilog=epilog)
    parser.add_argument('-c', '--config', action='store_true',
                        help="config file to use (default: {})".format(
                            configpath
                        ))
    parser.add_argument('-r', '--run', type=int,
                        help="which run to make: < 1 | 2 > ")
    parser.add_argument("--head",
                        help="Git ref to test (default: HEAD)")
    parser.add_argument("--base",
                        help="Git ref to diff against (default: master)")
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help="do everything except actually executing tests")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='suppress output')
    args = parser.parse_args()
    verbose = not args.quiet
    runid = getattr(args, 'run') or 0
    if runid not in [0, 1, 2]:
        raise ValueError("Invalid run argument: {}".format(runid))
    config = getattr(args, 'config') or configpath
    head = getattr(args, 'head') or 'HEAD'
    base = getattr(args, 'base') or 'origin/master'
    dryrun = args.dry_run
    if verbose:
        print("Fastest run:{} using config file {}".format(runid, config))
        print("Calculating changes in {} that are not in {}".format(
            head, base))

    try:
        changes = whatchanged(head, base, verbose)
    except RunAllTestsException:
        return run('', verbose=verbose, dryrun=dryrun)

    policy = Policy(config)
    (packages, tests) = policy(changes, verbose=verbose)
    spec_pkg = spec('-s', packages)
    spec_tst = spec('-t', tests)

    if packages and tests and runid in [0, 1]:
        return run_multi([spec_pkg, spec_tst], verbose=verbose, dryrun=dryrun)
    elif packages and runid in [0, 1]:
        return run(spec_pkg, verbose=verbose, dryrun=dryrun)
    elif tests and runid in [0, 1]:
        return run(spec_tst, verbose=verbose, dryrun=dryrun)
    elif packages or tests and runid == 2:
        # optimized run, we don't need the second run
        if verbose:
            print("Optimization OK, tests in run 1, nothing to do in run 2.")
        return 0

    # no optimization
    if not packages and not tests:
        if runid == 0:
            # jenkins combined run
            return run("", verbose=verbose, dryrun=dryrun)
        elif runid == 1:
            # gitlab run 1 of 2
            return run("-t '!robot'", verbose=verbose, dryrun=dryrun)
        else:
            # gitlab run 2 of 2
            return run("-t 'robot'", verbose=verbose, dryrun=dryrun)


def repo():
    """In case of a non-git (egg) release tests will be disabled"""
    return git.Repo(repo_dir)


def whatchanged(commitid, baseid=None, verbose=True):
    if not baseid:
        raise RunAllTestsException("No base to compare against")
    repo().git.fetch()  # update master index even if master sandbox is behind
    commit = repo().commit(commitid)
    base = repo().commit(baseid)
    # GOTCHA: what looks like a neat sequential history turns out to
    # be a more complex parenting history when merge commits are involved
    commit_and_parents = [commit]
    commit_parent_generator = commit.iter_parents()
    base_and_parents = [base]
    base_parent_generator = base.iter_parents()
    shared_ancestors = []
    commit_history_exhausted = base_history_exhausted = False
    while not commit_history_exhausted or not base_history_exhausted:
        try:
            commit_and_parents.append(next(commit_parent_generator))
        except StopIteration:
            commit_history_exhausted = True
        try:
            base_and_parents.append(next(base_parent_generator))
        except StopIteration:
            base_history_exhausted = True
        # massive speedup: stop backtracking on first shared parent
        shared_ancestors = [x for x in commit_and_parents
                            if x in base_and_parents]
        if shared_ancestors:
            break
    if not shared_ancestors:
        raise RunAllTestsException("No shared ancestors")
    # only test changes in HEAD that are not yet in master
    new_commits = [x for x in commit_and_parents if x not in base_and_parents]
    if not new_commits:
        # run full suite when testing master against master
        raise RunAllTestsException("Nothing changed, running full suite.")
    if verbose:
        print("Found {} new commits".format(len(new_commits)))
        if len(new_commits) <= 20:
            for _c in new_commits:
                print("    {:.10}   {:.50}".format(_c.hexsha, _c.summary))
    skip_commits = [x for x in new_commits if '[ci skip]' in x.summary]
    if skip_commits and verbose:
        print("Skipping {} commits marked as [ci skip]".format(
            len(skip_commits)))
    if skip_commits and new_commits == skip_commits:
        # only happens on a branch with minimal changes
        raise RunNoTestsException(
            "All changes marked as [ci skip], skipping all tests.")
    commit_diffs = [x.diff(x.parents[0]) for x in new_commits
                    if x not in skip_commits]
    # each commit diff contains an iterable of file diffs
    file_diffs = [f for c in commit_diffs for f in c]
    return {x.a_path or x.b_path for x in file_diffs}


def run(testspec, verbose=True, dryrun=False):
    # this is a bit of a hack to support both src and egg builds
    # and both bin/fastest and bin/test invocations
    buildout_dir = os.getcwd().replace('/parts/test', '')
    testrunner = os.path.join(buildout_dir, 'bin', 'test')
    command = '{} {}'.format(testrunner, testspec)
    if verbose:
        marker = dryrun and "Dryrun" or "Subprocess"
        print("{}: {}".format(marker, command))
    if dryrun:
        return 0
    try:
        process = subprocess.Popen(command, shell=True,
                                   stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output and verbose:
                print output.strip()
            if process.poll() is not None:
                break
        return process.poll()
    except subprocess.CalledProcessError, exc:
        if verbose:
            print("ERROR: return code {}")
        return exc.returncode


def run_multi(speclist, verbose=True, dryrun=False):
    status = 0
    for testspec in speclist:
        status += run(testspec, verbose, dryrun)
    return status
