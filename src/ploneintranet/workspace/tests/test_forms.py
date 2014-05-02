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

    def test_policy_form(self):
        """ Check that the policy form controls the policy
            settings correctly """
        self.login_as_portal_owner()
        workspace = api.content.create(
            self.portal,
            "ploneintranet.workspace.workspacefolder",
            "example-workspace",
            title="A workspace")

        # Form setup gubbins stolen from:
        # http://plone-testing-documentation.readthedocs.org/en/latest/z3c.form.html
        def make_request(form={}):
            request = TestRequest()
            request.form.update(form)
            alsoProvides(request, IFormLayer)
            alsoProvides(request, IAttributeAnnotatable)
            return request

        provideAdapter(adapts=(Interface, IBrowserRequest),
                       provides=Interface,
                       factory=PolicyForm,
                       name="policies")

        request = make_request(form={
            'form.buttons.ok': 'OK',
        })
        policyform = api.content.get_view('policies',
                                          context=workspace,
                                          request=request)
        policyform.update()
        data, errors = policyform.extractData()
        self.assertEqual(len(errors), 3)

        # Now give it some data
        request = make_request(form={
            'form.widgets.external_visibility': 'private',
            'form.widgets.join_policy': 'team',
            'form.widgets.participant_policy': 'moderators',
            'form.buttons.ok': 'OK',
        })
        policyform = api.content.get_view('policies',
                                          context=workspace,
                                          request=request)
        policyform.update()
        data, errors = policyform.extractData()
        self.assertEqual(len(errors), 0)

        self.assertEqual(workspace.external_visibility,
                         'private')
        self.assertEqual(workspace.join_policy,
                         'team')
        self.assertEqual(workspace.participant_policy,
                         'moderators')
