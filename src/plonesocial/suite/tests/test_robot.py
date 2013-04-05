import unittest
import robotsuite
from plonesocial.suite.testing import PLONESOCIAL_ROBOT_TESTING
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(robotsuite.RobotTestSuite('robot'),
                            layer=PLONESOCIAL_ROBOT_TESTING), ])
    return suite
