from plone import api
from ploneintranet.workspace.interfaces import IMetroMap
from ploneintranet.workspace.tests.base import FunctionalBaseTestCase
from ploneintranet.workspace.unrestricted import execute_as_manager
from zope.component import queryAdapter


class TestCaseWorkspace(FunctionalBaseTestCase):
    """A Case is a Workspace with some extra features, such as the metromap
    view and additional fields """

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        pwft = api.portal.get_tool("portal_placeful_workflow")
        workspaces = api.content.create(
            type="ploneintranet.workspace.workspacecontainer",
            title="Workspaces",
            container=self.portal,
        )
        self.case = api.content.create(
            type="ploneintranet.workspace.case",
            title="case1",
            container=workspaces,
        )
        self.case.manage_addProduct[
            'CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        wfconfig = pwft.getWorkflowPolicyConfig(self.case)
        wfconfig.setPolicyIn('case_workflow')

    def test_metromap_initial_state(self):
        """A newly created Case is in the first workflow state. It can't be
        finished and it must be possible to change workflow state to the next
        state, so the first transition is is_current.
        """
        mm_seq = IMetroMap(self.case).metromap_sequence
        initial_state_id = mm_seq.keys()[0]
        self.assertTrue(mm_seq[initial_state_id]["is_current"])
        self.assertFalse(mm_seq[initial_state_id]["finished"])

    def test_metromap_second_state(self):
        """After carrying out the first workflow transition, the first state is
        finished. If the workflow allows for it, the first transition could
        still be is_current. The second transition should be is_current.
        """
        mm_seq = IMetroMap(self.case).metromap_sequence
        first_state_id = mm_seq.keys()[0]
        first_transition = mm_seq[first_state_id]["transition_id"]
        api.content.transition(self.case, first_transition)

        mm_seq = IMetroMap(self.case).metromap_sequence
        self.assertTrue(mm_seq[first_state_id]["finished"])

        second_state_id = mm_seq.keys()[1]
        self.assertTrue(mm_seq[second_state_id]["is_current"])
        self.assertFalse(mm_seq[second_state_id]["finished"])

    def test_workspace_has_no_metromap(self):
        workspaces = api.content.create(
            type="ploneintranet.workspace.workspacecontainer",
            title="workspace1-container",
            container=self.portal,
        )
        workspace = api.content.create(
            type="ploneintranet.workspace.workspacefolder",
            title="workspace1",
            container=workspaces,
        )
        self.assertTrue(queryAdapter(workspace, IMetroMap) is None)

    def test_add_case_from_template(self):
        template = api.content.create(
            type='ploneintranet.workspace.case',
            id='template1',
            container=self.portal.templates,
        )
        api.content.create(
            type='Document',
            id='doc1',
            container=template,
        )
        case_request = self.request.clone()
        case_request['workspace-type'] = 'template1'
        add_workspace = api.content.get_view(
            'add_workspace',
            context=self.portal.workspaces,
            request=case_request,
        )
        add_workspace.title = u'Case from template'
        self.case = execute_as_manager(add_workspace.create_from_template)
        self.assertTrue('doc1' in self.portal.workspaces['case-from-template'])
