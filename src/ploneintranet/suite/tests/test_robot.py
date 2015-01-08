import unittest

# import robotsuite
# from ploneintranet.suite.testing import PLONEINTRANET_SUITE_ROBOT
# from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    # suite.addTests([
    #     layered(robotsuite.RobotTestSuite('test_hello.robot'),
    #             layer=PLONEINTRANET_SUITE_ROBOT),
    # ])
    return suite
