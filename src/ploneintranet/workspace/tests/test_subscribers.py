# -*- coding: utf-8 -*-
from collective.workspace.interfaces import IWorkspace
from plone import api
from ploneintranet.workspace.basecontent.utils import dexterity_update
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


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


class TestTitleFromID(BaseTestCase):
    """
        Tests that when content is pasted in the context of a workspace,
        the id will be generated based on the content's title, thus avoiding
        ids like `copy_of_`
    """

    def setUp(self):
        super(TestTitleFromID, self).setUp()
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

    def test_change_doc_title(self):
        self.doc1.REQUEST.form = {'title': u'My Døcümént olé'}
        modified, errors = dexterity_update(self.doc1)
        self.assertEqual(errors, [])
        notify(ObjectModifiedEvent(self.doc1))
        self.assertEquals(self.doc1.getId(), 'my-document-ole')

    def test_change_doc_title_updates_catalog(self):
        catalog = api.portal.get_tool('portal_catalog')
        self.assertEquals(len(catalog(getId='my-document')), 1)
        self.doc1.REQUEST.form = {'title': u'My totally renamed doc'}
        modified, errors = dexterity_update(self.doc1)
        self.assertEqual(errors, [])
        notify(ObjectModifiedEvent(self.doc1))
        self.assertEquals(self.doc1.getId(), 'my-totally-renamed-doc')
        self.assertEquals(len(catalog(getId='my-document')), 0)
        self.assertEquals(len(catalog(getId='my-totally-renamed-doc')), 1)
        self.assertEquals(len(catalog(Title='My totally renamed doc')), 1)

    def test_change_doc_long_title(self):
        self.doc1.REQUEST.form = dict(
            title=u"The quick brown fox jumps over the very lazy dog's back "
                  "after having stared at it undecidedly for hours.")
        modified, errors = dexterity_update(self.doc1)
        self.assertEqual(errors, [])
        notify(ObjectModifiedEvent(self.doc1))
        self.assertEquals(
            self.doc1.getId(),
            'the-quick-brown-fox-jumps-over-the-very-lazy-dogs-back-after-having'  # noqa
        )

    def test_file_title_does_not_change_id(self):
        file_obj = api.content.create(
            container=self.workspace,
            type='File',
            title=u'My File',
        )
        self.assertEquals(file_obj.getId(), 'my-file')
        file_obj.REQUEST.form = {'title': u'My süper File'}
        modified, errors = dexterity_update(file_obj)
        self.assertEqual(errors, [])
        notify(ObjectModifiedEvent(file_obj))
        self.assertEquals(file_obj.Title(), 'My s\xc3\xbcper File')
        self.assertEquals(file_obj.getId(), 'my-file')

    def test_change_folder_title(self):
        self.subfolder.REQUEST.form = {'title': u'My fäntästic Folder'}
        modified, errors = dexterity_update(self.subfolder)
        self.assertEqual(errors, [])
        notify(ObjectModifiedEvent(self.subfolder))
        self.assertEquals(self.subfolder.getId(), 'my-fantastic-folder')
