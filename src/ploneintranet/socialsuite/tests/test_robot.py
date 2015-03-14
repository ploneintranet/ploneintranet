import unittest
import robotsuite
from ploneintranet.socialsuite.testing import PLONEINTRANET_SOCIAL_ROBOT
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    # functional tests ARE run by default - we have no unit tests
    suite.addTests([layered(robotsuite.RobotTestSuite('functional'),
                            layer=PLONEINTRANET_SOCIAL_ROBOT), ])
    return suite
