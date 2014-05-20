from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import provideAdapter
from plone import api
from ploneintranet.workspace.tests.base import BaseTestCase
from ploneintranet.workspace.browser.forms import PolicyForm
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
                         'moderators')

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
