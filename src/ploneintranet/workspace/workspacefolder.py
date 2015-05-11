from collections import OrderedDict
from collections import defaultdict
from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.todo.behaviors import ITodo
from ploneintranet.workspace import MessageFactory
from ploneintranet.workspace.events import ParticipationPolicyChangedEvent
from ploneintranet.workspace.interfaces import ICase
from zope import schema
from zope.event import notify
from zope.interface import implementer


class IWorkspaceFolder(form.Schema, IImageScaleTraversable):
    """
    Interface for WorkspaceFolder
    """
    calendar_visible = schema.Bool(
        title=MessageFactory(u"label_workspace_calendar_visibility",
                             u"Calendar visible in central calendar"),
        required=False,
        default=False,
    )
    email = schema.TextLine(
        title=MessageFactory(u'label_workspace_email', u'E-mail address'),
        required=False,
        default=u'',
    )


@implementer(IWorkspaceFolder, IAttachmentStoragable)
class WorkspaceFolder(Container):
    """
    A WorkspaceFolder users can collaborate in
    """

    # Block local role acquisition so that users
    # must be given explicit access to the workspace
    __ac_local_roles_block__ = 1

    def acquire_workspace(self):
        """
        helper method to acquire the workspace
        :rtype: ploneintranet.workspace.WorkspaceFolder
        """
        return self

    @property
    def external_visibility(self):
        return api.content.get_state(self)

    def set_external_visibility(self, value):
        api.content.transition(obj=self, to_state=value)

    @property
    def is_case(self):
        return ICase.providedBy(self)

    @property
    def join_policy(self):
        try:
            return self._join_policy
        except AttributeError:
            return "admin"

    @join_policy.setter
    def join_policy(self, value):
        self._join_policy = value

    @property
    def participant_policy(self):
        try:
            return self._participant_policy
        except AttributeError:
            return "consumers"

    @participant_policy.setter
    def participant_policy(self, value):
        """ Changing participation policy fires a
        "ParticipationPolicyChanged" event
        """
        old_policy = self.participant_policy
        new_policy = value
        self._participant_policy = new_policy
        notify(ParticipationPolicyChangedEvent(self, old_policy, new_policy))

    def tasks(self):
        items = defaultdict(list) if self.is_case else []
        catalog = api.portal.get_tool('portal_catalog')
        current_path = '/'.join(self.getPhysicalPath())
        ptype = 'todo'
        brains = catalog(path=current_path, portal_type=ptype)
        for brain in brains:
            obj = brain.getObject()
            todo = ITodo(obj)
            data = {
                'id': brain.UID,
                'title': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'checked': todo.status == u'done'
            }
            if self.is_case:
                milestone = "unassigned"
                if obj.milestone not in ["", None]:
                    milestone = obj.milestone
                items[milestone].append(data)
            else:
                items.append(data)
        return items

    @property
    def metromap_sequence(self):
        """An ordered dict with the structure required for displaying tasks in the metromap and in
        the sidebar of a Case item
        OrderedDict([
            ("new", {
                "enabled": False, "transition_id": "transfer_to_department", "finished": True}),
            ("in_progress", {
                 "enabled": False, "transition_id": "transfer_to_department", "finished": True}),
        ])
        """
        wft = api.portal.get_tool("portal_workflow")
        case_workflows = [
            i for i in wft.getWorkflowsFor(self)
            if i.variables.get("metromap_transitions", False)
        ]
        if case_workflows == []:
            return {}
        # Assume we only have one
        cwf = case_workflows[0]
        metromap_transitions = [
            i.strip()
            for i in cwf.variables["metromap_transitions"].default_value.split(",")
        ]
        initial_state = cwf.initial_state
        initial_transition = metromap_transitions[0]
        available_transition_ids = [i["id"] for i in wft.getTransitionsFor(self)]
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
        for i in sequence:
            sequence[i]["finished"] = "unfinished"
        return sequence
