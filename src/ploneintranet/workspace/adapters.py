from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from borg.localrole.default_adapter import DefaultLocalRoleAdapter
from borg.localrole.interfaces import ILocalRoleProvider
from collections import OrderedDict
from collective.workspace.interfaces import IHasWorkspace
from collective.workspace.workspace import Workspace
from plone import api
from ploneintranet.workspace.interfaces import ICase
from ploneintranet.workspace.interfaces import IMetroMap
from zope.component import adapts
from zope.interface import implements


class PloneIntranetWorkspace(Workspace):
    """
    A custom workspace behaviour, based on collective.workspace

    Here we define our own available groups, and the roles
    they are given on the workspace.
    """

    # A list of groups to which team members can be assigned.
    # Maps group name -> roles
    available_groups = {
        u'Admins': ('Contributor', 'Editor', 'Reviewer',
                    'Reader', 'TeamManager',),
        u'Members': ('TeamMember', ),
        # These are the 'participation policy' groups
        u'Consumers': (),
        u'Producers': ('Contributor',),
        u'Publishers': ('Contributor', 'SelfPublisher',),
        u'Moderators': ('Reader', 'Contributor', 'Reviewer', 'Editor',),
    }

    def add_to_team(self, **kw):
        """
        We override this method to add our additional participation
        policy groups, as detailed in available_groups above
        """
        group = self.context.participant_policy.title()
        data = kw.copy()
        if "groups" in data:
            data["groups"].add(group)
        else:
            data["groups"] = set([group])

        super(PloneIntranetWorkspace, self).add_to_team(**data)

    def group_for_policy(self, policy=None):
        """
        Lookup the collective.workspace usergroup corresponding to the
        given policy

        :param policy: The value of the policy to lookup, defaults to the
                       current policy
        :type policy: str
        """
        if policy is None:
            policy = self.context.participant_policy
        return "%s:%s" % (policy.title(), self.context.UID())


class WorkspaceLocalRoleAdapter(DefaultLocalRoleAdapter):
    """
    If the user has the local role of Owner on the context
    and the acquired role of SelfPublisher; they should also be given Reviewer.

    """
    implements(ILocalRoleProvider)
    adapts(IContentish)

    def getRoles(self, principal_id):
        """
        give an Owner who is also a 'selfpublisher', the reviewer role
        """
        context = self.context
        current_roles = list(DefaultLocalRoleAdapter.getRoles(
            self,
            principal_id,
        ))

        # check we are not on the workspace itself
        if IHasWorkspace.providedBy(context):
            return current_roles
        # otherwise we should acquire the workspace and check out roles
        workspace = getattr(context, 'acquire_workspace', lambda: None)()
        if workspace is None:
            return current_roles

        workspace_roles = api.user.get_roles(obj=workspace)
        if 'SelfPublisher' in workspace_roles and 'Owner' in current_roles:
            current_roles.append('Reviewer')
        return current_roles


class MetroMap(object):
    implements(IMetroMap)
    adapts(IFolderish)

    def __init__(self, context):
        self.context = context

    @property
    def _metromap_workflow(self):
        wft = api.portal.get_tool("portal_workflow")
        metromap_workflows = [
            i for i in wft.getWorkflowsFor(self.context)
            if i.variables.get("metromap_transitions", False)
        ]
        import pdb; pdb.set_trace()
        if metromap_workflows == []:
            return None
        # Assume we only have one
        import pdb; pdb.set_trace()
        return metromap_workflows

    def get_available_metromap_workflows(self):
        wft = api.portal.get_tool('portal_workflow')
        metromap_workflows = [
            i for i in wft.objectValues()
            if i.variables.get("metromap_transitions", False)
        ]
        import pdb; pdb.set_trace()
        if metromap_workflows == []:
            return None
        # Assume we only have one
        return metromap_workflows

    @property
    def _metromap_transitions(self):
        metromap_workflow = self._metromap_workflow
        if metromap_workflow is None:
            return []
        metromap_transitions = [
            i.strip()
            for i in metromap_workflow.variables["metromap_transitions"].default_value.split(",")
        ]
        return metromap_transitions

    @property
    def metromap_sequence(self):
        cwf = self._metromap_workflow
        wft = api.portal.get_tool("portal_workflow")
        metromap_transitions = self._metromap_transitions
        if not metromap_transitions:
            return {}
        initial_state = cwf.initial_state
        initial_transition = metromap_transitions[0]
        available_transition_ids = [i["id"] for i in wft.getTransitionsFor(self.context)]
        sequence = OrderedDict({
            initial_state: {
                "transition_id": initial_transition,
                "enabled": initial_transition in available_transition_ids,
            }
        })
        for index, transition_id in enumerate(metromap_transitions):
            transition = cwf.transitions.get(transition_id, "")
            next_state = transition.new_state_id
            #new_state_id if new_state_id in cwf.states.objectIds() else "unassigned"
            next_transition = ""
            if index + 1 < len(metromap_transitions):
                next_transition = metromap_transitions[index + 1]
            sequence[next_state] = {
                "transition_id": next_transition,
                "enabled": next_transition in available_transition_ids,
            }
        current_state = wft.getInfoFor(self.context, "review_state")
        finished = True
        for state in sequence.keys():
            if state == current_state:
                finished = False
            sequence[state]["finished"] = finished
        return sequence
