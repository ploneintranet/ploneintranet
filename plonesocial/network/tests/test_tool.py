import unittest2 as unittest
from zope.component import queryUtility

from plone.app.testing import TEST_USER_ID, setRoles

from plonesocial.network.testing import \
    PLONESOCIAL_NETWORK_INTEGRATION_TESTING

from plonesocial.network.interfaces import INetworkGraph
from plonesocial.network.interfaces import INetworkTool


class TestNetworkTool(unittest.TestCase):

    layer = PLONESOCIAL_NETWORK_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_tool_available(self):
        tool = queryUtility(INetworkTool)
        self.assertTrue(INetworkGraph.providedBy(tool))
