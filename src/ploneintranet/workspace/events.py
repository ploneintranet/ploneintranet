from zope.interface import implements

from ploneintranet.workspace.interfaces import IParticipationPolicyChangedEvent


class ParticipationPolicyChangedEvent(object):
    """ Event class, which is fired once the participation policy
    of the workspace has changed
    """
    implements(IParticipationPolicyChangedEvent)

    def __init__(self, ob, old_policy, new_policy):
        self.workspace = ob
        self.old_policy = old_policy
        self.new_policy = new_policy
