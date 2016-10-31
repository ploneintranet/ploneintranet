# coding=utf-8
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from ploneintranet.workspace.interfaces import IWorkspaceAppContentLayer
from ploneintranet.workspace.testing import PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING  # noqa
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder


class TestMail(BaseTestCase):
    """ Test the Mailin feature
    """
    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        super(TestMail, self).setUp()
        alsoProvides(self.request, IWorkspaceAppContentLayer)
        self.mail_workspace = workspace_folder = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'mail-workspace',
            title='Workspace title'
        )
        self.mail = api.content.create(
            workspace_folder,
            'ploneintranet.workspace.mail',
            title='A mail from a customer',
        )
        self.mail.mail_from = u'sender@example.com'
        self.mail.mail_to = (
            u'recipient1@example.com',
        )
        self.mail.mail_cc = (u'cc1@example.com', u'cc2@example.com')
        self.mail.mail_bcc = (u'bcc1@example.com', u'bcc2@example.com')
        self.mail.mail_body = RichTextValue(
            u'<b>Hello world</b>',
        )
        api.content.create(
            self.mail,
            'File',
            title='Attachment 1',
        )
        api.content.create(
            self.mail,
            'Image',
            title='Attachment 2',
        )

    def get_request(self):
        ''' Return a fresh request
        '''
        request = self.request.clone()
        alsoProvides(request, IWorkspaceAppContentLayer)
        return request

    def test_mail_content(self):
        """ Test the fields and the attributes of this content type
        """
        self.assertTrue(self.mail.disable_add_from_sidebar)
        fields = []
        [
            fields.extend(x[0] for x in getFieldsInOrder(schemata))
            for schemata in iterSchemata(self.mail)
        ]
        self.assertListEqual(
            fields,
            [
                'title',
                'description',
                'mail_from',
                'mail_to',
                'mail_cc',
                'mail_bcc',
                'mail_body',
                'subjects',
                'language'
            ]
        )

    def test_mail_view(self):
        """ Test the view of this content type
        """
        view = api.content.get_view(
            'mail_view',
            self.mail,
            self.get_request(),
        )
        self.assertEqual(
            view.sidebar_target,
            'workspace-documents',
        )
        view()

    def test_mail_copy(self):
        """ Test the view to copy the mail attachments
        """
        view = api.content.get_view(
            'copy-attachments-to-workspace',
            self.mail,
            self.get_request(),
        )
        view()
        self.assertListEqual(
            sorted(self.mail_workspace.keys()),
            [
                '.wf_policy_config',
                'a-mail-from-a-customer',
                'attachment-1',
                'attachment-2',
            ]
        )

    def test_attachment_copy(self):
        """ Test the view to copy an attachment
        """

        view = api.content.get_view(
            'copy-to-workspace',
            self.mail['attachment-1'],
            self.get_request(),
        )
        view()
        self.assertListEqual(
            sorted(self.mail_workspace.keys()),
            [
                '.wf_policy_config',
                'a-mail-from-a-customer',
                'attachment-1',
            ]
        )
