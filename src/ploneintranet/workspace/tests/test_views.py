from AccessControl import Unauthorized
from ploneintranet.workspace.browser.views import JoinView
from collective.workspace.interfaces import IWorkspace
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase


class TestSelfJoin(BaseTestCase):

    def setUp(self):
        super(TestSelfJoin, self).setUp()
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.login_as_portal_owner()
        self.workspace = api.content.create(
            self.portal,
            "ploneintranet.workspace.workspacefolder",
            "demo-workspace",
            title="Demo Workspace")
        self.user = api.user.create(
            email="demo@example.org",
            username="demo",
            password="demon",
            )

    def open_workspace(self):
        self.workspace.join_policy = "self"
        self.workspace.visibility = "open"

    def test_user_can_join(self):
        self.open_workspace()
        self.request.method = "POST"
        self.request.form = {"button.join": True}
        self.request["HTTP_REFERER"] = "someurl"
        self.login("demo")
        view = JoinView(self.workspace, self.request)
        response = view()
        self.assertEqual("someurl", response)
        self.assertIn("demo", IWorkspace(self.workspace).members)

    def test_user_cant_join_if_policy_is_not_self(self):
        self.login("demo")
        view = JoinView(self.workspace, self.request)
        self.assertRaises(Unauthorized, view)

    def test_user_redirected_if_method_get(self):
        self.open_workspace()
        self.request.method = "GET"
        self.request.form = {"button.join": True}
        self.request["HTTP_REFERER"] = "someurl"
        self.login("demo")
        view = JoinView(self.workspace, self.request)
        response = view()
        self.assertEqual("someurl", response)
        self.assertNotIn("demo", IWorkspace(self.workspace).members)

    def test_user_redirected_to_workspace_if_no_referer(self):
        self.open_workspace()
        self.login("demo")
        view = JoinView(self.workspace, self.request)
        response = view()
        self.assertEqual(self.workspace.absolute_url(), response)
