from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase


class TestWorkflow(BaseTestCase):

    def test_default_workflow(self):
        """the ploneintranet workflow should be set as the default workflow"""
        wftool = api.portal.get_tool('portal_workflow')
        self.assertIn('ploneintranet_workflow',
                      wftool.listWorkflows())
