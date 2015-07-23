import unittest

import robotsuite
from ploneintranet.search.solr.testing import ROBOT_TESTING
from ploneintranet.search.solr.testing import SOLR_ENABLED
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    if SOLR_ENABLED:
        suite.addTests([
            layered(robotsuite.RobotTestSuite('search.robot'),
                    layer=ROBOT_TESTING),
        ])
    return suite
