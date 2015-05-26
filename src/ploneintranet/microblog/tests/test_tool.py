import unittest2 as unittest
from zope.component import queryUtility

from plone import api

from ploneintranet.microblog.testing import \
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

from ploneintranet.microblog.interfaces import IStatusContainer
from ploneintranet.microblog.interfaces import IMicroblogTool


class TestMicroblogTool(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_tool_available(self):
        tool = queryUtility(IMicroblogTool)
        self.assertTrue(IStatusContainer.providedBy(tool))

    def test_tool_uninstalled(self):
        qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            qi.uninstallProducts(products=['ploneintranet.microblog'])
        self.assertNotIn('ploneintranet_microblog', self.portal)
        tool = queryUtility(IMicroblogTool, None)
        self.assertIsNone(tool)
