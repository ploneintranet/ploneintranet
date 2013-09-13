import unittest
import robotsuite
from plonesocial.suite.testing import PLONESOCIAL_ROBOT_TESTING
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    demo_suite = robotsuite.RobotTestSuite("demo")
    # demo disabled by default, to run use: bin/test -a 2
    demo_suite.level = 2
    suite.addTests([layered(demo_suite,
                            layer=PLONESOCIAL_ROBOT_TESTING), ])
    # functional tests ARE run by default - we have no unit tests
    suite.addTests([layered(robotsuite.RobotTestSuite('functional'),
                            layer=PLONESOCIAL_ROBOT_TESTING), ])
    return suite
