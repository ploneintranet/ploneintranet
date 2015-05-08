from AccessControl import Unauthorized
from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.widgets.browser.file import FileUploadView as BaseFileUploadView
from plone.app.workflow.browser.sharing import SharingView as BaseSharingView
from plone.memoize.forever import memoize
from Products.Five.browser import BrowserView
from zope.interface import implements

from ploneintranet.workspace import MessageFactory as _
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from ploneintranet.workspace.interfaces import IWorkspaceState
from ploneintranet.workspace.utils import parent_workspace


class JoinView(BrowserView):
    """
    adds a user to the team on a self-join workspace
    """

    def __call__(self):
        if not self.context.join_policy == "self":
            msg = _(u"Workspace join policy doesn't allow self join")
            raise Unauthorized(msg)

        field = "button.join"
        req_method = self.request.method.lower()
        if req_method == "post" and field in self.request.form:
            user = api.user.get_current()
            workspace = IWorkspace(self.context)
            workspace.add_to_team(user=user.getId())
            msg = _(u"You are a member of this workspace now")
            api.portal.show_message(message=_(msg),
                                    request=self.request)

        referer = self.request.get("HTTP_REFERER", "").strip()
        if not referer:
            referer = self.context.absolute_url()
        return self.request.response.redirect(referer)


class SharingView(BaseSharingView):
    """
    override the sharing tab
    """

    def can_edit_inherit(self):
        """ Disable "inherit permissions" checkbox """
        return False

    def role_settings(self):
        """ Filter out unwanted to show groups """
        result = super(SharingView, self).role_settings()
        uid = self.context.UID()
        filter_func = lambda x: not any((
            x["id"].endswith(uid),
            x["id"] == "AuthenticatedUsers",
            x["id"] == INTRANET_USERS_GROUP_ID,
        ))
        return filter(filter_func, result)

    def user_search_results(self):
        """ Add [member] to a user title if user is a member
        of current workspace
        """
        results = super(SharingView, self).user_search_results()
        ws = IWorkspace(self.context)
        roles_mapping = ws.available_groups
        roles = roles_mapping.get(self.context.participant_policy.title())

        for result in results:
            if result["id"] in ws.members:
                groups = ws.get(result["id"]).groups
                for role in roles:
                    result["roles"][role] = "acquired"
                if "Admins" in groups:
                    title = "administrator"
                    result["roles"]["TeamManager"] = "acquired"
                else:
                    title = "member"
                result["title"] = "%s [%s]" % (result["title"], title)

        return results


class FileUploadView(BaseFileUploadView):
    """Redirect to the workspace view so we can inject."""
    def __call__(self):
        result = {}
        if self.request.get('file', ''):
            result = super(FileUploadView, self).__call__()
        accept = self.request.get_header('HTTP_ACCEPT')
        if accept == 'text/json':
            return result
        else:
            self.request.response.redirect(self.context.absolute_url())
