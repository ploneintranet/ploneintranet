from Products.Five.browser import BrowserView
from plone import api
from collective.workspace.interfaces import IWorkspace
from AccessControl import Unauthorized
from plone.app.workflow.browser.sharing import SharingView as BaseSharingView

from ploneintranet.workspace import MessageFactory as _
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID


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
        for result in results:
            if result["id"] in ws.members:
                result["title"] = "%s [member]" % result["title"]
        return results
