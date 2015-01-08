from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_ROBOT_TESTING
from plone.testing import layered
import robotsuite
import unittest

# I outcomment these tests as they were written for barceloneta. 
# We need to 
#  a) Rewrite them for ploneintranet.theme and
#  b) Move them to ploneintranet.suite so that we can test for all integrated packages.
# We don't delete them yet so that we have a reference

# def test_suite():
#     suite = unittest.TestSuite()
#     suite.addTests([
#         layered(robotsuite.RobotTestSuite("workspace.robot"),
#                 layer=PLONEINTRANET_WORKSPACE_ROBOT_TESTING)
#     ])
#     return suite
