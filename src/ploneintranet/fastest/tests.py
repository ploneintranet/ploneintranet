import unittest
from git import InvalidGitRepositoryError
from ploneintranet.fastest import (repo, whatchanged,
                                   Strategy, Policy,
                                   spec,
                                   run, run_multi)


class TestFastest(unittest.TestCase):

    def setUp(self):
        try:
            repo()
        except InvalidGitRepositoryError:
            self.skipTest("Not in a git repo (egg release?)")

        self.ws_strategy = Strategy("workspace")
        self.ws_strategy.packages = ['ploneintranet.workspace']
        self.ws_strategy.tests = ['workspace', 'shoppingcart']
        self.ws_strategy.triggers = ['src/ploneintranet/workspace']
        self.mb_strategy = Strategy("microblog")
        self.mb_strategy.packages = ['ploneintranet.microblog',
                                     'ploneintranet.activitystream']
        self.mb_strategy.tests = ['posting', 'content_discussion']
        self.mb_strategy.triggers = ['src/ploneintranet/microblog',
                                     'src/ploneintranet/activitystream']

    def test_whatchanged_default(self):
        newest = 'df89786574a4dca504e77f92704aa6b157fea313'
        changed = whatchanged(newest)
        expect = {
            'src/ploneintranet/layout/browser/passwordpanel.py',
            'src/ploneintranet/layout/browser/templates/personal-menu.pt',
            'src/ploneintranet/layout/viewlets/personalbar.py'
        }
        self.assertEquals(changed, expect)

    def test_whatchanged_explicit(self):
        newest = 'df89786574a4dca504e77f92704aa6b157fea313'
        since = 'efe14a393a0540a2dea8e737310f9faa0896bd75'
        changed = whatchanged(newest, since)
        expect = {
            'src/ploneintranet/layout/browser/passwordpanel.py',
            'src/ploneintranet/layout/browser/templates/personal-menu.pt',
            'src/ploneintranet/layout/viewlets/personalbar.py'
        }
        self.assertEquals(changed, expect)

    def test_strategy_nomatch(self):
        changed = {
            'src/ploneintranet/layout/browser/passwordpanel.py',
            'src/ploneintranet/layout/browser/templates/personal-menu.pt',
            'src/ploneintranet/layout/viewlets/personalbar.py'
        }
        (packages, tests) = self.ws_strategy(changed, verbose=False)
        self.assertEquals((set(), set()), (packages, tests))

    def test_strategy_matchall(self):
        changed = {
            'src/ploneintranet/workspace/workspacefolder.py',
            'src/ploneintranet/workspace/browser/configure.zcml',
        }
        (packages, tests) = self.ws_strategy(changed, verbose=False)
        self.assertEquals(({'ploneintranet.workspace'},
                           {'workspace', 'shoppingcart'}),
                          (packages, tests))

    def test_policy_ws(self):
        policy = Policy(self.ws_strategy, self.mb_strategy)
        changed = {
            'src/ploneintranet/workspace/workspacefolder.py',
            'src/ploneintranet/workspace/browser/configure.zcml',
        }
        (packages, tests) = policy(changed, verbose=False)
        self.assertEquals(({'ploneintranet.workspace'},
                           {'workspace', 'shoppingcart'}),
                          (packages, tests))

    def test_policy_both(self):
        policy = Policy(self.ws_strategy, self.mb_strategy)
        changed = {
            'src/ploneintranet/workspace/workspacefolder.py',
            'src/ploneintranet/microblog/browser/__init__.py',
        }
        (packages, tests) = policy(changed, verbose=False)
        self.assertEquals(({'ploneintranet.workspace',
                            'ploneintranet.microblog',
                            'ploneintranet.activitystream'},
                           {'workspace', 'shoppingcart',
                            'posting', 'content_discussion'}),
                          (packages, tests))

    def test_policy_mismatch(self):
        policy = Policy(self.ws_strategy, self.mb_strategy)
        changed = {
            'src/ploneintranet/workspace/workspacefolder.py',
            'src/ploneintranet/microblog/browser/__init__.py',
            'src/ploneintranet/no/such/thing'
        }
        (packages, tests) = policy(changed, verbose=False)
        self.assertEquals((set(), set()), (packages, tests))

    def test_wildcard(self):
        policy = Policy(self.ws_strategy, self.mb_strategy)
        strategy = Strategy("wildcard")
        strategy.wildcard = True
        strategy.triggers = 'setup.py'
        policy.add(strategy)
        changed = {
            'src/ploneintranet/workspace/workspacefolder.py',
            'src/ploneintranet/microblog/browser/__init__.py',
            'setup.py'
        }
        (packages, tests) = policy(changed, verbose=False)
        self.assertEquals((set(), set()), (packages, tests))

    def test_spec(self):
        self.assertEquals("-s foo -s bar",
                          spec('-s', {'foo', 'bar'}))

    def test_run(self):
        testspec = "-s ploneintranet.fastest -t noop"
        self.assertEquals(0, run(testspec, verbose=False))

    def test_run_multi(self):
        testspec = ["-s ploneintranet.fastest -t noop",
                    "-s ploneintranet.fastest -t noop"]
        self.assertEquals(0, run_multi(testspec, verbose=False))

    def test_noop(self):
        # avoid a test_run infinite recursion loop
        self.assertTrue(True)


if __name__ == '__main__':
    import unittest
    unittest.main()
