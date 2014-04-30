from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from collective.workspace.interfaces import IHasWorkspace, IWorkspace


class TestContentTypes(BaseTestCase):

    def create_workspace(self):
        """ returns adapted workspace folder"""
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')
        return IWorkspace(workspace_folder)

    def create_unadapted_workspace(self):
        """ Return unadapted workspace object """
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')
        return workspace_folder

    def create_user(self, name="testuser", password="secret"):
        user = api.user.create(
            email="test@user.com",
            username=name,
            password=password,
            )
        return user

    def test_add_workspacefolder(self):
        """ check that we can create our workspace folder type,
            and that it provides the collective.workspace behaviour
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace')

        self.assertTrue(
            IHasWorkspace.providedBy(workspace_folder),
            'Workspace type does not provide the'
            'collective.workspace behaviour',
        )

        # does the view work?
        view = workspace_folder.restrictedTraverse('@@view')
        html = view()
        self.assertIn(workspace_folder.title, html,
                      'Workspace title not found on view page')

    def test_add_user_to_workspace(self):
        """ check that we can add a new user to a workspace """
        self.login_as_portal_owner()
        ws = self.create_workspace()
        user = self.create_user()
        ws.add_to_team(user=user)
        self.assertEqual(len(ws.members), 1)
        self.assertEqual(list(ws.members)[0].getUserName(), 'testuser')

    def test_add_admin_to_workspace(self):
        """ check that site admin can add team admin to the workspace """
        self.login_as_portal_owner()
        ws = self.create_unadapted_workspace()
        user = self.create_user()
        groups = api.group.get_groups()
        group_names = [x.getName() for x in groups]
        group_name = "Admins:%s" % (api.content.get_uuid(ws))
        self.assertIn(
            group_name,
            group_names)
        workspace = IWorkspace(ws)
        workspace.add_to_team(user=user, groups=set([u"Admins"]))

        portal = api.portal.get()
        pgroups = portal.portal_groups.getGroupById(group_name)
        members = pgroups.getGroup().getMemberIds()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].getId(), user.getId())
