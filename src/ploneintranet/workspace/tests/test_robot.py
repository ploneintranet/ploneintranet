from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_ROBOT_TESTING
from plone.testing import layered
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("workspace.robot"),
                layer=PLONEINTRANET_WORKSPACE_ROBOT_TESTING)
    ])
    return suite
