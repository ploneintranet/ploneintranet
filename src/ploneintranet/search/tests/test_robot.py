import unittest

import robotsuite
from ploneintranet.search.testing import ROBOT_TESTING
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite('search.robot'),
                layer=ROBOT_TESTING),
    ])
    return suite
