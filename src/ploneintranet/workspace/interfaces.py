from zope.interface import Attribute, Interface


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


class ICase(Interface):
    """A marker interface to differentiate between a Workspace and a Case
    """


class IMetroMap(Interface):
    """Methods required to display a metromap
    """

    def metromap_workflow():
        """In order to display the metromap for Case Workspaces, a workflow with a
        "metromap_transitions" variable must be in the workflow chain.
        For now, let's assume we only have one workflow in the chain, so return the first one.
        """

    def metromap_transitions():
        """Since a metromap is linear, we need a sequence of workflow transitions to represent the
        lifecycle of a Case. A comma separated string variable ("metromap_transitions") is stored
        on the workflow. Extract this and return the transitions as a list.
        """

    def metromap_sequence(self):
        """An ordered dict with the structure required for displaying tasks in the metromap and in
        the sidebar of a Case item. This is used to determine which states have been finished, and
        which transitions are currently available.
        OrderedDict([
            ("new", {
                "enabled": False, "transition_id": "transfer_to_department", "finished": True}),
            ("in_progress", {
                 "enabled": False, "transition_id": "transfer_to_department", "finished": True}),
        ])
        """
