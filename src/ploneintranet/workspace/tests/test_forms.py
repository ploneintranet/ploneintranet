from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase


class TestPolicyForm(BaseTestCase):

    def test_policy_form(self):
        """ Basic test to check that the policy form renders """
        self.login_as_portal_owner()
        workspace = api.content.create(
            self.portal,
            "ploneintranet.workspace.workspacefolder",
            "example-workspace",
            title="A workspace")

        form = api.content.get_view('policies',
                                    context=workspace,
                                    request=self.request)
