from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.app.layout.viewlets import ViewletBase


class JoinViewlet(ViewletBase):
    def in_workspace(self):
        return hasattr(self.context, "acquire_workspace")

    def visible(self):
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
        workspace = self.context.acquire_workspace()
        return "%s/%s" % (workspace.absolute_url(), "joinme")
