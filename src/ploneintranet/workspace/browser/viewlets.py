from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.app.layout.viewlets import ViewletBase
from ploneintranet.workspace.policies import PARTICIPANT_POLICY


class JoinViewlet(ViewletBase):
    """ Allows users to join a self-joining workspace """

    def in_workspace(self):
        """
        Are we currently in a workspace?
        """
        return hasattr(self.context, "acquire_workspace")

    def visible(self):
        """
        Join viewlet is shown if:
        * In a 'self-join' workspace
        * User is not already a member
        """
        if not self.in_workspace():
            return False

        if not self.context.join_policy == "self":
            return False

        user = api.user.get_current()
        workspace = IWorkspace(self.context.acquire_workspace())
        if user.getUserName() in workspace.members:
            return False

        return True

    def join_url(self):
        """
        Get url of the join action
        """
        workspace = self.context.acquire_workspace()
        return "%s/%s" % (workspace.absolute_url(), "joinme")


class SharingViewlet(ViewletBase):
    """
    Provides information about the default policy when viewing
    the sharing tab on a workspace.
    """

    def visible(self):
        """
        Only shown on the sharing view
        """
        context_state = api.content.get_view(context=self.context,
                                             request=self.request,
                                             name="plone_context_state")
        url = context_state.current_base_url()
        return url.endswith('@@sharing')

    def active_participant_policy(self):
        """ Get the title of the current participation policy """
        key = self.context.participant_policy
        policy = PARTICIPANT_POLICY.get(key)
        return policy['title']
