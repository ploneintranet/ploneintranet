from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from plone.app.testing import login
from plone.app.testing import logout
import unittest

VIEW = 'View'
MODIFY = 'Modify portal content'
DELETE = 'Delete objects'

"""
This tests the workflow of content in a case.
"""


class CaseContentBaseTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.login_as_portal_owner()
        api.user.create(username='wsadmin', email="admin@test.com")
        api.user.create(username='wsmember', email="member@test.com")
        api.user.create(username='nonmember', email="user@test.com")
        self.workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.case',
            'example-case',
            title='Welcome to my case')
        self.add_user_to_workspace('wsmember', self.workspace_folder)
        self.add_user_to_workspace('wsadmin', self.workspace_folder,
                                   set(['Admins']))
        self.document = api.content.create(
            self.workspace_folder,
            'Document',
            'document1')
        login(self.portal, 'wsmember')
        # wsmember is owner of document2
        self.document2 = api.content.create(
            self.workspace_folder,
            'Document',
            'document2')
        self.login_as_portal_owner()

    def admin_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='wsadmin',
            obj=self.document,
        )
        return permissions[permission]

    def member_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document,
        )
        return permissions[permission]

    def owner_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='wsmember',
            obj=self.document2,
        )
        return permissions[permission]

    def nonmember_permissions(self, permission):
        permissions = api.user.get_permissions(
            username='nonmember',
            obj=self.document,
        )
        return permissions[permission]

    def anon_permissions(self, permission):
        logout()
        permissions = api.user.get_permissions(
            obj=self.document,
        )
        return permissions[permission]


class New_CaseContentWorkflow(CaseContentBaseTestCase):

    @unittest.skip("Which applies: case_workflow or ploneintranet_workflow?")
    def test_draft_state(self):
        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(MODIFY))
        self.assertTrue(self.admin_permissions(DELETE))

        self.assertFalse(self.member_permissions(VIEW))
        self.assertFalse(self.member_permissions(MODIFY))
        self.assertFalse(self.member_permissions(DELETE))

        self.assertTrue(self.owner_permissions(VIEW))
        self.assertTrue(self.owner_permissions(MODIFY))
        self.assertTrue(self.owner_permissions(DELETE))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(DELETE))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(DELETE))

    @unittest.skip("Which applies: case_workflow or ploneintranet_workflow?")
    def test_pending_state(self):
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document2, 'submit')

        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(MODIFY))
        self.assertTrue(self.admin_permissions(DELETE))

        self.assertTrue(self.member_permissions(VIEW))
        self.assertFalse(self.member_permissions(MODIFY))
        self.assertFalse(self.member_permissions(DELETE))

        self.assertTrue(self.owner_permissions(VIEW))
        self.assertFalse(self.owner_permissions(MODIFY))
        self.assertFalse(self.owner_permissions(DELETE))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(DELETE))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(DELETE))

    @unittest.skip("Which applies: case_workflow or ploneintranet_workflow?")
    def test_published_state(self):
        api.content.transition(self.document, 'submit')
        api.content.transition(self.document, 'publish')
        api.content.transition(self.document2, 'submit')
        api.content.transition(self.document2, 'publish')

        self.assertTrue(self.admin_permissions(VIEW))
        self.assertTrue(self.admin_permissions(MODIFY))
        self.assertTrue(self.admin_permissions(DELETE))

        self.assertTrue(self.member_permissions(VIEW))
        self.assertFalse(self.member_permissions(MODIFY))
        self.assertFalse(self.member_permissions(DELETE))

        self.assertTrue(self.owner_permissions(VIEW))
        self.assertFalse(self.owner_permissions(MODIFY))
        self.assertFalse(self.owner_permissions(DELETE))

        self.assertFalse(self.nonmember_permissions(VIEW))
        self.assertFalse(self.nonmember_permissions(MODIFY))
        self.assertFalse(self.nonmember_permissions(DELETE))

        self.assertFalse(self.anon_permissions(VIEW))
        self.assertFalse(self.anon_permissions(MODIFY))
        self.assertFalse(self.anon_permissions(DELETE))


class Prepare_CaseContentWorkflow(New_CaseContentWorkflow):

    def setUp(self):
        New_CaseContentWorkflow.setUp(self)
        api.content.transition(self.workspace_folder,
                               'assign')


class Complete_CaseContentWorkflow(New_CaseContentWorkflow):

    def setUp(self):
        New_CaseContentWorkflow.setUp(self)
        api.content.transition(self.workspace_folder,
                               'assign')
        api.content.transition(self.workspace_folder,
                               'finalise')


class Audit_CaseContentWorkflow(New_CaseContentWorkflow):

    def setUp(self):
        New_CaseContentWorkflow.setUp(self)
        api.content.transition(self.workspace_folder,
                               'assign')
        api.content.transition(self.workspace_folder,
                               'finalise')
        api.content.transition(self.workspace_folder,
                               'request')


class Propose_CaseContentWorkflow(New_CaseContentWorkflow):

    def setUp(self):
        New_CaseContentWorkflow.setUp(self)
        api.content.transition(self.workspace_folder,
                               'assign')
        api.content.transition(self.workspace_folder,
                               'finalise')
        api.content.transition(self.workspace_folder,
                               'request')
        api.content.transition(self.workspace_folder,
                               'submit')


class Decided_CaseContentWorkflow(New_CaseContentWorkflow):

    def setUp(self):
        New_CaseContentWorkflow.setUp(self)
        api.content.transition(self.workspace_folder,
                               'assign')
        api.content.transition(self.workspace_folder,
                               'finalise')
        api.content.transition(self.workspace_folder,
                               'request')
        api.content.transition(self.workspace_folder,
                               'submit')
        api.content.transition(self.workspace_folder,
                               'decide')


class Closed_CaseContentWorkflow(New_CaseContentWorkflow):

    def setUp(self):
        New_CaseContentWorkflow.setUp(self)
        api.content.transition(self.workspace_folder,
                               'assign')
        api.content.transition(self.workspace_folder,
                               'finalise')
        api.content.transition(self.workspace_folder,
                               'request')
        api.content.transition(self.workspace_folder,
                               'submit')
        api.content.transition(self.workspace_folder,
                               'decide')
        api.content.transition(self.workspace_folder,
                               'close')


class Archived_CaseContentWorkflow(New_CaseContentWorkflow):

    def setUp(self):
        New_CaseContentWorkflow.setUp(self)
        api.content.transition(self.workspace_folder,
                               'assign')
        api.content.transition(self.workspace_folder,
                               'finalise')
        api.content.transition(self.workspace_folder,
                               'request')
        api.content.transition(self.workspace_folder,
                               'submit')
        api.content.transition(self.workspace_folder,
                               'decide')
        api.content.transition(self.workspace_folder,
                               'close')
        api.content.transition(self.workspace_folder,
                               'archive')
