from zope.interface import implements
from zope.component.interfaces import ObjectEvent

from ploneintranet.workspace.interfaces import IParticipationPolicyChangedEvent
from ploneintranet.workspace.interfaces import IWorkspaceRosterChangedEvent


class ParticipationPolicyChangedEvent(ObjectEvent):
    """ Event class, which is fired once the participation policy
    of the workspace has changed
    """
    implements(IParticipationPolicyChangedEvent)

    def __init__(self, ob, old_policy, new_policy):
        super(ParticipationPolicyChangedEvent, self).__init__(ob)
        self.old_policy = old_policy
        self.new_policy = new_policy


class WorkspaceRosterChangedEvent(ObjectEvent):
    """
    Event, which is fired once the roster of a workspace had changed
    """
    implements(IWorkspaceRosterChangedEvent)

    def __init__(self, ob):
        super(WorkspaceRosterChangedEvent, self).__init__(ob)
