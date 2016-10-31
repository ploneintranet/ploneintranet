# coding=utf-8
import os
from ploneintranet.workspace.tests.base import BaseTestCase
from plone import api
from plone.api.exc import InvalidParameterError
from plone.namedfile.file import NamedBlobImage
from collective.workspace.interfaces import IHasWorkspace, IWorkspace

from ploneintranet.workspace.config import TEMPLATES_FOLDER
from ploneintranet.workspace.browser.add_workspace import AddWorkspace


class TestAddWorkspace(BaseTestCase):

    def test_add_workspacefolder(self):
        """ check that we can create our workspace folder type,
            and that it provides the collective.workspace behaviour
        """
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title=u'Welcome to my workspacé'
        )

        self.assertTrue(
            IHasWorkspace.providedBy(workspace_folder),
            'Workspace type does not provide the'
            'collective.workspace behaviour',
        )

        # does the view work?
        view = workspace_folder.restrictedTraverse('@@view')
        html = view()
        self.assertIn(
            workspace_folder.title,
            html,
            'Workspace title not found on view page'
        )

    def test_cannot_add_workspace_in_portal(self):
        """
        workspaces cannot be nested
        """
        self.login_as_portal_owner()
        self.assertRaises(
            InvalidParameterError,
            api.content.create,
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'banned-workspace',
        )

    def test_cannot_add_sub_workspace(self):
        """
        workspaces cannot be nested
        """
        self.login_as_portal_owner()
        workspace = api.content.create(
            container=self.workspace_container,
            type='ploneintranet.workspace.workspacefolder',
            id='workspace-1',
        )
        self.assertRaises(
            InvalidParameterError,
            api.content.create,
            workspace,
            'ploneintranet.workspace.workspacefolder',
            'workspace-2',
        )

    def test_add_workspacecontainer(self):
        """
        Check that WorkspaceContainer can be added to site root
        """
        self.login_as_portal_owner()
        api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'test-workspaces',
            title='Test Workspaces'
        )
        self.assertIn('test-workspaces', self.portal)

    def test_cannot_add_workspacecontainer_inside_workspace(self):
        """
        Check that WorkspaceContainer cannot be added inside a workspace
        """
        self.login_as_portal_owner()
        ws = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'workspace-1',
            title='Workspace 1'
        )
        self.assertRaises(
            InvalidParameterError,
            api.content.create,
            ws,
            'ploneintranet.workspace.workspacecontainer',
            'workspace-container',
        )

    def test_can_add_workspace_inside_workspacecontainer(self):
        """
        Check that workspaces can be added inside workspace container.
        The workspace container is already being added in the setuphandler.
        """
        self.login_as_portal_owner()
        wsc = getattr(self.portal, 'workspaces')
        api.content.create(
            wsc,
            'ploneintranet.workspace.workspacefolder',
            'workspace-1',
            title='Workspace 1'
        )
        self.assertIn('workspace-1', wsc)

    def test_cannot_add_other_content_in_workspacecontainer(self):
        """
        Check that *only* workspaces can be added inside workspace container
        """
        self.login_as_portal_owner()
        wsc = getattr(self.portal, 'workspaces')
        self.assertRaises(
            InvalidParameterError,
            api.content.create,
            wsc,
            'Document',
            'doc-1',
        )

    def test_attributes(self):
        """
        Check that we can access and set the attributes
        """
        self.login_as_portal_owner()
        wsc = getattr(self.portal, 'workspaces')
        ws = api.content.create(
            wsc,
            'ploneintranet.workspace.workspacefolder',
            'workspace-1',
            title='Workspace 1'
        )
        self.assertEqual(ws.calendar_visible, False)
        self.assertEqual(ws.email, '')

        ws.calendar_visible = True
        ws.email = 'test@testing.net'

        self.assertEqual(ws.calendar_visible, True)
        self.assertEqual(ws.email, 'test@testing.net')

        self.assertEqual(ws.hero_image, None)

        filename = os.path.join(os.path.dirname(__file__), u'hero_image.jpg')
        data = open(filename, 'r').read()
        ws.hero_image = NamedBlobImage(
            data=data,
            filename=filename
        )

        self.assertEqual(len(ws.hero_image.data), len(data))


class TestAddWorkspaceView(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        api.user.create(username='johndoe', email="johndoe@test.com")
        api.user.create(username='maryjane', email="maryjane@test.com")
        self.templates_container = self.portal.get(TEMPLATES_FOLDER)
        self.template = api.content.create(
            self.templates_container,
            'ploneintranet.workspace.workspacefolder',
            'example-template',
            title='Welcome to my workspace template'
        )
        self.add_user_to_workspace('johndoe', self.template)

    def test_AddWorkspaceView(self):
        self.login('johndoe')
        request = self.layer['request'].clone()
        request.form['workspace-type'] = 'private'
        request.form['title'] = 'my workspace'
        aw = AddWorkspace(self.workspace_container, request)
        aw()
        self.assertIn('my-workspace',
                      self.workspace_container.objectIds())

    def test_add_template_via_view(self):
        request = self.layer['request'].clone()
        request.form['workspace-type'] = 'private'
        request.form['title'] = 'my template'
        at = AddWorkspace(self.templates_container, request)
        at()
        self.assertIn('my-template',
                      self.templates_container.objectIds())
        request = self.layer['request'].clone()
        aw = AddWorkspace(self.workspace_container, request)
        self.assertIn('my-template', aw.all_templates_dict)

    def test_template_member_can_see_template_in_menu(self):
        self.login('johndoe')
        request = self.layer['request'].clone()
        aw = AddWorkspace(self.templates_container, request)
        self.assertIn('example-template', aw.all_templates_dict)

    def test_template_nonmember_cannot_see_template_in_menu(self):
        self.login('maryjane')
        request = self.layer['request'].clone()
        aw = AddWorkspace(self.templates_container, request)
        self.assertNotIn('example-template', aw.all_templates_dict)


class TestAddUsersToWorkspace(BaseTestCase):

    def _create_workspace(self):
        """ returns adapted workspace folder"""
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace'
        )
        return IWorkspace(workspace_folder)

    def _create_unadapted_workspace(self):
        """ Return unadapted workspace object """
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace',
            title='Welcome to my workspace'
        )
        return workspace_folder

    def _create_user(self, name='testuser', password='secret'):
        """
        helper method for creating a test user
        :param name: username
        :param password: password for the user
        :returns: user object
        :rtype: MemberData

        """
        user = api.user.create(
            email='test@user.com',
            username=name,
            password=password,
        )
        return user

    def test_add_user_to_workspace(self):
        """ check that we can add a new user to a workspace """
        self.login_as_portal_owner()
        ws = self._create_workspace()
        user = self._create_user()
        ws.add_to_team(user=user.getId())
        self.assertIn(user.getId(),
                      [x for x in list(ws.members)])

    def test_add_admin_to_workspace(self):
        """ check that site admin can add team admin to the workspace """
        self.login_as_portal_owner()
        ws = self._create_unadapted_workspace()
        user = self._create_user()
        groups = api.group.get_groups()
        group_names = [x.getName() for x in groups]
        group_name = 'Admins:%s' % (api.content.get_uuid(ws))
        self.assertIn(
            group_name,
            group_names
        )
        workspace = IWorkspace(ws)
        workspace.add_to_team(user=user.getId(), groups=set([u"Admins"]))

        portal = api.portal.get()
        pgroups = portal.portal_groups.getGroupById(group_name)
        member_ids = pgroups.getGroup().getMemberIds()
        self.assertIn(user.getId(),
                      member_ids)
