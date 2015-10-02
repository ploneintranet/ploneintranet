from zope.interface import Attribute
from zope.interface import Interface

from ploneintranet.layout import interfaces as ilayout


class IPloneintranetWorkspaceLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class IWorkspaceAppContentLayer(ilayout.IPloneintranetContentLayer,
                                ilayout.IAppLayer):
    """Marker interface for content within a workspace app."""


class IWorkspaceAppFormLayer(ilayout.IPloneintranetFormLayer,
                             ilayout.IAppLayer):
    """Marker interface for forms within a workspace app."""


class IParticipationPolicyChangedEvent(Interface):
    """ Event, which is fired once the participation policy
    of the workspace has changed
    """
    old_policy = Attribute(u"Policy we are moving away from")
    new_policy = Attribute(u"Policy we are moving to")


class IWorkspaceRosterChangedEvent(Interface):
    """
    Event, which is fired once the roster of a workspace had changed
    """


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


class IMetroMap(Interface):
    """Methods required to display a metromap
    """

    def get_available_metromap_workflows():
        """In order to display the metromap for Case Workspaces, a workflow
        with a "metromap_transitions" variable must be in the workflow chain.

        Since a metromap is linear, we need a sequence of workflow
        transitions to represent the lifecycle of a Case. A comma separated
        string variable ("metromap_transitions") is stored on the
        workflow. Extract this and return the transitions as a list.
        """

    def metromap_sequence():
        """An ordered dict with the structure required for displaying tasks in
        the metromap and in the sidebar of a Case item. This is used to
        determine which states have been finished, and
        which transitions are currently available.
        OrderedDict([(
            "new", {
                "is_current": False,
                "transition_id": "transfer_to_department",
                "finished": True,
            }), (
            "in_progress", {
                "is_current": False,
                "transition_id": "transfer_to_department",
                "finished": True,
            }),
        ])
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
