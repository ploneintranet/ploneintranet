import unittest

import robotsuite
from plone.intranet.suite.testing import PLONE_INTRANET_SUITE_ROBOT
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite('test_hello.robot'),
                layer=PLONE_INTRANET_SUITE_ROBOT),
    ])
    return suite
