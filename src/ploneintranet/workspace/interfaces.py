from zope.interface import Attribute
from zope.interface import Interface


class IParticipationPolicyChangedEvent(Interface):
    """ Event, which is fired once the participation policy
    of the workspace has changed
    """
    old_policy = Attribute(u"Policy we are moving away from")
    new_policy = Attribute(u"Policy we are moving to")


class IWorkspaceState(Interface):
    """A view that gives access to the containing workspace
    """

    def workspace():
        """
        The workspace
        """

    def state():
        """
        The state of the workspace
        """


class IGroupingStoragable(Interface):
    """marker interface for things that can have a GroupingStorage
    """


class IGroupingStorage(Interface):

    def update_groupings(obj):
        """ Update the groupings dict with the values stored on obj.
        """

    def remove_from_groupings(obj):
        """ Remove obj's grouping relevant information to its workspace.
        """

    def reset_order():
        """ Reset the order for all groupings to default, i.e. same order
            as the keys of the OOBTree
        """

    def get_order_for(grouping,
                      include_archived=False,
                      alphabetical=False):
        """ Get order for a given grouping
        """

    def set_order_for(grouping, order):
        """ Set order for a given grouping
        """

    def get_groupings():
        """ Return groupings
        """
