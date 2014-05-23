from collective.workspace.interfaces import IWorkspace
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import provideAdapter
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.browser.forms import PolicyForm
from ploneintranet.workspace.browser.forms import TransferMembershipForm
from z3c.form.interfaces import IFormLayer
from zope.publisher.browser import TestRequest
from zope.interface import alsoProvides
from zope.annotation.interfaces import IAttributeAnnotatable


class TestPolicyForm(BaseTestCase):

    # Form setup gubbins stolen from:
    # http://plone-testing-documentation.readthedocs.org/en/latest/z3c.form.html  # noqa
    def make_request(self, empty=False, visibility="secret",
                     join_policy="team", participant_policy="Moderators"):
        """ Creates a request
        :param bool empty: if true, request will be empty, any other given \
                      parameters will be ignored
        :param str visibility: what workspace visibility should be set. \
                               Default is "secret"
        :param str join_policy: Set the join policy on a workspace. Default \
                                is "team".
        :param str participant_policy: Set the participation policy param.\
                                       Default is "moderators".
        :return: submitted request.
        """

        if empty:
            form = {'form.buttons.ok': 'OK'}
        else:
            form = {
                'form.widgets.external_visibility': visibility,
                'form.widgets.join_policy': join_policy,
                'form.widgets.participant_policy': participant_policy,
                'form.buttons.ok': 'OK',
            }

        request = TestRequest()
        request.form.update(form)
        alsoProvides(request, IFormLayer)
        alsoProvides(request, IAttributeAnnotatable)
        return request

    def test_policy_form(self):
        """ Check that the policy form controls the policy
            settings correctly """
        self.login_as_portal_owner()
        workspace = api.content.create(
            self.portal,
            "ploneintranet.workspace.workspacefolder",
            "example-workspace",
            title="A workspace")

        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=PolicyForm,
                       name="policies")

        request = self.make_request(empty=True)

        policyform = api.content.get_view('policies',
                                          context=workspace,
                                          request=request)
        policyform.update()
        data, errors = policyform.extractData()
        self.assertEqual(len(errors), 3)

        # Now give it some data
        request = self.make_request()
        policyform = api.content.get_view('policies',
                                          context=workspace,
                                          request=request)
        policyform.update()
        data, errors = policyform.extractData()
        self.assertEqual(len(errors), 0)

        self.assertEqual(workspace.external_visibility,
                         api.content.get_state(obj=workspace))

        self.assertEqual(workspace.join_policy,
                         'team')
        self.assertEqual(workspace.participant_policy,
                         'Moderators')

        # Now give it some data
        request = self.make_request(visibility="open")

        policyform = api.content.get_view('policies',
                                          context=workspace,
                                          request=request)
        policyform.update()
        data, errors = policyform.extractData()
        self.assertEqual(len(errors), 0)

        self.assertEqual(workspace.external_visibility,
                         api.content.get_state(obj=workspace))


class TestTransferForm(BaseTestCase):

    # Form setup gubbins stolen from:
    # http://plone-testing-documentation.readthedocs.org/en/latest/z3c.form.html  # noqa
    def make_request(self, ws_uid, move=False):
        """ Creates a request
        :param str ws_uid: workspace uid to transfer users to
        :param bool move: if True, delete from current workspace
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

    def create_user(self, name="testuser", password="secret"):
        """ Creates a request
        :param str name: username, default="testuser"
        :param str password: password, default="secret"
        :return: user object
        """

        user = api.user.create(
            email=name + "@user.com",
            username=name,
            password=password,
            )
        return user

    def test_transfer_form(self):
        """ Check that the transfer form can copy/move users
            to another workspace """
        self.login_as_portal_owner()

        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=TransferMembershipForm,
                       name="transfer")

        ws = api.content.create(
            self.portal,
            "ploneintranet.workspace.workspacefolder",
            "alejandro-workspace",
            title="Alejandro workspace")

        names = "Dima Nikita Alex Vlad Sergey".split()
        for name in names:
            IWorkspace(ws).add_to_team(
                user=self.create_user(name=name).getId())

        # subtracting admin from members list
        self.assertEqual(len(names), len(list(IWorkspace(ws).members))-1)

        other_ws = api.content.create(
            self.portal,
            "ploneintranet.workspace.workspacefolder",
            "isabella-workspace",
            "Isabella Workspace",)

        # copy users
        request = self.make_request(api.content.get_uuid(other_ws))
        transfer_form = api.content.get_view('transfer',
                                             context=ws,
                                             request=request)
        transfer_form.update()
        data, errors = transfer_form.extractData()
        self.assertEqual(len(errors), 0)

        self.assertEqual(len(names), len(list(IWorkspace(ws).members))-1)
        self.assertEqual(len(names), len(list(IWorkspace(other_ws).members))-1)

        # now move users
        # WARNING: browser creates a proper checkbox field in the form,
        # while test makes it as a radio button. For selected
        # checkbox value should be: [u"selected"], and selected radio
        # has a value of ["true"]
        request = self.make_request(api.content.get_uuid(other_ws), True)
        form = api.content.get_view('transfer',
                                    context=ws,
                                    request=request)
        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

        self.assertEqual(len(names), len(list(IWorkspace(other_ws).members))-1)
        self.assertEqual(0, len(list(IWorkspace(ws).members)))

        # now move users back
        request = self.make_request(api.content.get_uuid(ws), True)
        form = api.content.get_view('transfer',
                                    context=other_ws,
                                    request=request)
        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

        self.assertEqual(0, len(list(IWorkspace(other_ws).members)))
        self.assertEqual(len(names), len(list(IWorkspace(ws).members))-1)
