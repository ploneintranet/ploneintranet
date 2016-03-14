import unittest
import os
import robotsuite
from ploneintranet.suite.testing import PLONEINTRANET_SUITE_SOLR_ROBOT
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    for testfile in os.listdir(
            os.path.join(os.path.dirname(__file__), "acceptance")):
        testfilepath = os.path.join("acceptance", testfile)
        if os.path.isdir(testfilepath):
            continue
        # work around layer conflict by running ALL tests on solr layer
        if testfile.endswith('.robot'):
            suite.addTests([
                layered(
                    robotsuite.RobotTestSuite(
                        testfilepath,
                        noncritical=['fixme']),
                    layer=PLONEINTRANET_SUITE_SOLR_ROBOT),
            ])
    return suite
