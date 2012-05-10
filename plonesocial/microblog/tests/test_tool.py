import unittest2 as unittest
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID, setRoles

from plonesocial.microblog.testing import \
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plonesocial.microblog.interfaces import IStatusContainer
from plonesocial.microblog.interfaces import IMicroblogTool


class TestMicroblogTool(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_tool_available(self):
        tool = queryUtility(IMicroblogTool)
        self.assertTrue(IStatusContainer.providedBy(tool))
