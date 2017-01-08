# -*- coding: utf-8 -*-
from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from plone import api
from collective.workspace.interfaces import IWorkspace


class TestSubscribers(BaseTestCase):

    def test_workspace_state_changed(self):
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        roles = api.group.get_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace_folder,
        )
        self.assertNotIn('Guest', roles)

        # Transition to open should add the role
        api.content.transition(obj=workspace_folder,
                               to_state='open')
        roles = api.group.get_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace_folder,
        )
        self.assertIn('Guest', roles)

        # Transition to another state should remove it
        api.content.transition(obj=workspace_folder,
                               to_state='private')
        roles = api.group.get_roles(
            groupname=INTRANET_USERS_GROUP_ID,
            obj=workspace_folder,
        )
        self.assertNotIn('Guest', roles)


class TestUserDeletion(BaseTestCase):
    """ Test user deletion from site (not a workspace) """

    def setUp(self):
        super(TestUserDeletion, self).setUp()
        self.login_as_portal_owner()

        self.ws = api.content.create(
            self.workspace_container,
            "ploneintranet.workspace.workspacefolder",
            "alejandro-workspace",
            title="Alejandro workspace")

    def test_user_deletion_from_site_removes_from_workspace(self):
        username = "johnsmith"
        api.user.create(
            email="user@example.org",
            username=username,
            password="doesntmatter",
        )

        # there shouldn't be any minus admin user in workspace
        self.assertEqual(0, len(list(IWorkspace(self.ws).members)) - 1)

        # lets add one user
        self.add_user_to_workspace(username, self.ws)
        self.assertEqual(1, len(list(IWorkspace(self.ws).members)) - 1)

        # now lets remove a user from the site
        api.user.delete(username)

        # and this user should be gone from workspace as well
        self.assertEqual(0, len(list(IWorkspace(self.ws).members)) - 1)


class TestContentPaste(BaseTestCase):
    """
        Tests that when content is pasted in the context of a workspace,
        the id will be generated based on the content's title, thus avoiding
        ids like `copy_of_`
    """

    def setUp(self):
        super(TestContentPaste, self).setUp()
        self.login_as_portal_owner()
        workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace')
        self.workspace = workspace_folder

        self.doc1 = api.content.create(
            container=self.workspace,
            type='Document',
            title=u'My Døcümént',
        )
        self.subfolder = api.content.create(
            container=self.workspace,
            type='Folder',
            title=u'This is a subfolder',
        )

    def test_paste_document(self):
        cp = self.workspace.manage_copyObjects(ids=self.doc1.getId())
        self.workspace.manage_pasteObjects(cp)
        self.assertIn('my-document-1', self.workspace.objectIds())

    def test_paste_folder(self):
        cp = self.workspace.manage_copyObjects(ids=self.subfolder.getId())
        self.workspace.manage_pasteObjects(cp)
        self.assertIn('this-is-a-subfolder-1', self.workspace.objectIds())

    def test_paste_multiple(self):
        cp = self.workspace.manage_copyObjects(ids=self.doc1.getId())
        self.subfolder.manage_pasteObjects(cp)
        self.subfolder.manage_pasteObjects(cp)
        self.subfolder.manage_pasteObjects(cp)
        self.assertEquals(
            self.subfolder.objectIds(),
            ['my-document', 'my-document-1', 'my-document-2'])

    def test_paste_outside_workspace(self):
        cp = self.workspace.manage_copyObjects(ids=self.doc1.getId())
        self.portal.manage_pasteObjects(cp)
        self.portal.manage_pasteObjects(cp)
        self.assertIn('my-document', self.portal.objectIds())
        self.assertIn('copy_of_my-document', self.portal.objectIds())

    def test_always_take_id_from_title_1(self):
        cp = self.workspace.manage_copyObjects(ids=self.doc1.getId())
        self.subfolder.manage_pasteObjects(cp)
        self.subfolder.manage_pasteObjects(cp)
        # When we copy the copy...
        cp = self.subfolder.manage_copyObjects(ids='my-document-1')
        self.subfolder.manage_pasteObjects(cp)
        # ...then we don't end up with an id like my-document-1-1 but with
        # a generated id in continuation of the existing ids.
        self.assertEquals(
            self.subfolder.objectIds(),
            ['my-document', 'my-document-1', 'my-document-2'])

    def test_always_take_id_from_title_2(self):
        cp = self.workspace.manage_copyObjects(ids=self.doc1.getId())
        self.workspace.manage_pasteObjects(cp)
        # When we copy the copy...
        cp = self.workspace.manage_copyObjects(ids='my-document-1')
        # ...and paste it into the subfolder that does not have an item with
        # the original id yet...
        self.subfolder.manage_pasteObjects(cp)
        # ...then it gets pasted with the freshly generated id from the title.
        self.assertEquals(self.subfolder.objectIds(), ['my-document'])
