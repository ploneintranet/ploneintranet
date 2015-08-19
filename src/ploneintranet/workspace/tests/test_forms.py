# coding=utf-8
"""
Tests for ploneintranet.workspace forms
"""

from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.MailHost.interfaces import IMailHost
from collective.workspace.interfaces import IWorkspace
from email import message_from_string
from plone import api
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from ploneintranet.invitations.events import TokenAccepted
from ploneintranet.workspace.browser.forms import InviteForm
from ploneintranet.workspace.browser.forms import TransferMembershipForm
from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_FUNCTIONAL_TESTING
from ploneintranet.workspace.tests.base import BaseTestCase
from z3c.form.interfaces import IFormLayer
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getUtility
from zope.component import provideAdapter
from zope.event import notify
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
import re


class TestTransferForm(BaseTestCase):
    # Form setup gubbins stolen from:
    # http://plone-testing-documentation.readthedocs.org/en/latest/z3c.form.html  # noqa
    def make_request(self, ws_uid, move=False):
        """
        Creates a request

        :param ws_uid: the UID of the workspace to transfer to
        :type ws_uid: str
        :param move: whether to move or copy the members
        :type move: bool
        :return: submitted request.
        """

        # WARNING: browser creates a proper checkbox field in the form,
        # while test makes it as a radio button. For selected
        # checkbox value should be: [u"selected"], and selected radio
        # has a value of ["true"]

        form = {
            'form.widgets.workspace': [ws_uid],
            'form.widgets.move': [str(move).lower()],
            'form.buttons.ok': 'Ok',
        }

        request = TestRequest()
        request.form.update(form)
        alsoProvides(request, IFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        return request

    def create_user(self, name='testuser', password='secret'):
        """
        Creates a request

        :param name: username of the created user
        :type name: str
        :param password: password for the created user
        :type password: str
        :return: user object
        """
        user = api.user.create(
            email=name + '@user.com',
            username=name,
            password=password,
        )
        return user

    def test_transfer_form(self):
        """
        Check that the transfer form can copy/move users
        to another workspace
        """
        self.login_as_portal_owner()

        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=TransferMembershipForm,
                       name="transfer")

        ws = api.content.create(
            self.workspace_container,
            "ploneintranet.workspace.workspacefolder",
            "alejandro-workspace",
            title="Alejandro workspace")

        names = "Dima Nikita Alex Vlad Sergey".split()
        for name in names:
            IWorkspace(ws).add_to_team(
                user=self.create_user(name=name).getId()
            )

        # subtracting admin from members list
        self.assertEqual(len(names), len(list(IWorkspace(ws).members)) - 1)

        other_ws = api.content.create(
            self.workspace_container,
            "ploneintranet.workspace.workspacefolder",
            "isabella-workspace",
            "Isabella Workspace",)

        # copy users
        request = self.make_request(api.content.get_uuid(other_ws))
        transfer_form = api.content.get_view(
            'transfer',
            context=ws,
            request=request
        )
        transfer_form.update()
        data, errors = transfer_form.extractData()
        self.assertEqual(len(errors), 0)

        self.assertEqual(len(names), len(list(IWorkspace(ws).members)) - 1)
        self.assertEqual(
            len(names), len(list(IWorkspace(other_ws).members)) - 1)

        # now move users
        # WARNING: browser creates a proper checkbox field in the form,
        # while test makes it as a radio button. For selected
        # checkbox value should be: [u"selected"], and selected radio
        # has a value of ["true"]
        request = self.make_request(api.content.get_uuid(other_ws), True)
        form = api.content.get_view(
            'transfer',
            context=ws,
            request=request
        )
        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

        self.assertEqual(len(names),
                         len(list(IWorkspace(other_ws).members)) - 1)
        self.assertEqual(0, len(list(IWorkspace(ws).members)))

        # now move users back
        request = self.make_request(api.content.get_uuid(ws), True)
        form = api.content.get_view(
            'transfer',
            context=other_ws,
            request=request
        )
        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

        self.assertEqual(0, len(list(IWorkspace(other_ws).members)))
        self.assertEqual(len(names), len(list(IWorkspace(ws).members)) - 1)


class TestInvitationFormValidation(BaseTestCase):

    def setUp(self):
        super(TestInvitationFormValidation, self).setUp()
        self.login_as_portal_owner()
        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=InviteForm,
                       name="invite")

        self.ws = api.content.create(
            self.workspace_container,
            'ploneintranet.workspace.workspacefolder',
            'alejandro-workspace',
            title=u'Aléjandro workspace'
        )

    def create_user(self, name='auser', email='em@exa.org', password='secret'):
        """
        Creates a request

        :param name: username for the created user
        :type name: str
        :param email: email address for the created user
        :type email: str
        :param password: password for the created user
        :type password: str
        :return: user object
        """
        user = api.user.create(
            email=email,
            username=name,
            password=password,
        )
        return user

    # Form setup gubbins stolen from:
    # http://plone-testing-documentation.readthedocs.org/en/latest/z3c.form.html  # noqa
    def make_request(self, username=None, empty=False):
        """
        Creates a request

        :param username: username to invite
        :type username: str
        :param empty: if true, request will be empty, any other given
                      parameters will be ignored
        :type empty: bool
        :return: ready to submit request.
        """

        if empty:
            form = {'form.buttons.ok': 'OK'}
        else:
            form = {
                'form.widgets.user': username,
                'form.buttons.ok': 'OK',
            }

        request = TestRequest()
        request.form.update(form)
        alsoProvides(request, IFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        return request

    def test_user_with_no_email_is_not_accepted(self):
        username = 'muhammad'
        user = self.portal['acl_users']._doAddUser(
            username,
            '',
            ['AuthenticatedUser'],
            []
        )
        self.assertEqual(user.getProperty('email'), '')
        request = self.make_request(username=username)
        form = api.content.get_view(
            'invite',
            context=self.ws,
            request=request,
        )
        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 1)

    def test_empty_form_shows_an_error(self):
        request = self.make_request(empty=True)
        form = api.content.get_view(
            'invite',
            context=self.ws,
            request=request,
        )

        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 1)

    def test_form_doesnt_accept_a_ws_member_email(self):
        email = "vlad@example.org"
        username = 'vladislav'
        self.create_user(name='vladislav', email=email)
        self.add_user_to_workspace('vladislav', self.ws)
        # there should be one user minus admin
        self.assertEqual(1, len(list(IWorkspace(self.ws).members)) - 1)

        request = self.make_request(username=username)
        form = api.content.get_view(
            'invite',
            context=self.ws,
            request=request,
        )

        form.update()
        error_msg = "User is already a member of this workspace"
        self.assertEqual(
            error_msg,
            form.widgets['user'].error.message
        )

    def test_our_event_handler_doesnt_handle_not_our_events(self):
        # shouldn't happen anything, especially there shouldn't be
        # a key error
        notify(TokenAccepted("randomness"))


class TestInvitationFormEmailing(BaseTestCase):

    layer = PLONEINTRANET_WORKSPACE_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestInvitationFormEmailing, self).setUp()
        self.login_as_portal_owner()
        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=InviteForm,
                       name="invite")

        # create a workspace
        self.ws = api.content.create(
            self.workspace_container,
            "ploneintranet.workspace.workspacefolder",
            "alejandro-workspace",
            title="Alejandro workspace")

        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # don't import this at the top, because it screws up the setup
        # and none of the tests can run
        from Products.CMFPlone.tests.utils import MockMailHost
    #    # Mock the mail host so we can test sending the email
        mockmailhost = MockMailHost('MailHost')

        if not hasattr(mockmailhost, 'smtp_host'):
            mockmailhost.smtp_host = 'localhost'

        self.portal.MailHost = mockmailhost
        sm = self.portal.getSiteManager()
        sm.registerUtility(component=mockmailhost, provided=IMailHost)

        self.mailhost = api.portal.get_tool('MailHost')
        registry = getUtility(IRegistry)
        self.mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        self.mail_settings.email_from_name = u'Portal Owner'
        self.mail_settings.email_from_address = 'sender@example.org'

    def make_request(self, username, message=''):
        """
        Creates a request

        :param username: username of the invitee
        :type username: str
        :param message: additional message to be sent to the invitee
        :type message: str
        :return: ready to submit request.
        """
        form = {
            'form.widgets.user': username,
            'form.widgets.message': message,
            'form.buttons.ok': 'OK',
        }

        request = TestRequest()
        request.form.update(form)
        alsoProvides(request, IFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        return request

    def test_invitation_send_if_all_above_conditions_met(self):
        email = "vlad@example.org"
        username = 'vladislav'
        api.user.create(
            email=email,
            username=username,
            password='whatever',
        )
        # there shouldn't be any minus admin user in workspace
        self.assertEqual(0, len(list(IWorkspace(self.ws).members)) - 1)

        request = self.make_request(username=username)
        form = api.content.get_view(
            'invite',
            context=self.ws,
            request=request,
        )

        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)
        # no errors on the widget?
        self.assertEqual(form.widgets['user'].error, None)
        # our mock mail host received one email?
        self.assertEqual(len(self.mailhost.messages), 1)
        msg = message_from_string(self.mailhost.messages[0])
        # mail is actually received by correct recipient
        self.assertEqual(msg['To'], email)
        body = msg.get_payload()
        url_match = re.search("(?P<url>http://[0-9a-z:/@-]+)(?=\n)", body)
        self.assertNotEqual(url_match, None)
        url = url_match.groupdict('url').get('url')

        self.mailhost.reset()
        import transaction
        transaction.commit()

        browser = Browser(self.app)
        browser.open(url)
        self.assertIn('userrole-authenticated', browser.contents,
                      'User was not authenticated after accepting token')
        # check that user is added to workspace
        self.assertEqual(1, len(list(IWorkspace(self.ws).members)) - 1)

    def test_invitation_message_is_sent(self):
        email = "vlad@example.org"
        username = 'vladislav'
        api.user.create(
            email=email,
            username=username,
            password='whatever',
        )

        message = u'Hello and join my wörkspace'
        request = self.make_request(username=username, message=message)
        form = api.content.get_view(
            'invite',
            context=self.ws,
            request=request,
        )

        form.update()
        form.extractData()
        self.assertEqual(len(self.mailhost.messages), 1)
        msg = message_from_string(self.mailhost.messages[0])
        # mail is actually received by correct recipient
        self.assertEqual(msg['To'], email)
        body = msg.get_payload(decode=True)
        self.assertIn(message, body.decode('utf-8'))

    def test_if_empty_message_no_text_is_included(self):
        email = "vlad@example.org"
        username = 'vladislav'
        api.user.create(
            email=email,
            username=username,
            password='whatever',
        )

        request = self.make_request(username=username)
        form = api.content.get_view(
            'invite',
            context=self.ws,
            request=request,
        )

        optional = u'Here is the message from %s\n\n' % username
        form.update()
        self.assertEqual(len(self.mailhost.messages), 1)
        msg = message_from_string(self.mailhost.messages[0])
        # mail is actually received by correct recipient
        self.assertEqual(msg['To'], email)
        body = msg.get_payload()
        self.assertNotIn(optional, body)

    def test_invitation_send_but_user_became_a_member_not_via_link(self):
        email = "vlad@example.org"
        username = 'vladislav'
        api.user.create(
            email=email,
            username=username,
            password='whatever',
        )
        # there shouldn't be any minus admin user in workspace
        self.assertEqual(0, len(list(IWorkspace(self.ws).members)) - 1)

        request = self.make_request(username=username)
        form = api.content.get_view(
            'invite',
            context=self.ws,
            request=request,
        )

        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)
        # no errors on the widget?
        self.assertEqual(form.widgets['user'].error, None)
        # our mock mail host received one email?
        self.assertEqual(len(self.mailhost.messages), 1)
        msg = message_from_string(self.mailhost.messages[0])
        # mail is actually received by correct recipient

        # now lets add this user to workspace via other channels
        self.add_user_to_workspace(username, self.ws)

        self.assertEqual(msg['To'], email)
        body = msg.get_payload()
        url_match = re.search("(?P<url>http://[0-9a-z:/@-]+)(?=\n)", body)
        self.assertNotEqual(url_match, None)
        url = url_match.groupdict("url").get("url")

        self.mailhost.reset()
        import transaction
        transaction.commit()

        browser = Browser(self.app)
        browser.open(url)
        self.assertIn('userrole-authenticated', browser.contents,
                      'User was not authenticated after accepting token')
        # check that user is added to workspace
        self.assertEqual(1, len(list(IWorkspace(self.ws).members)) - 1)
        self.assertIn(
            "Oh boy, oh boy, you are already a member",
            browser.contents)
