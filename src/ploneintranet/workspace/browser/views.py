from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.app.content.browser.file import FileUploadView as BaseFileUploadView
from plone.app.dexterity.interfaces import IDXFileFactory
from plone.app.workflow.browser.sharing import SharingView as BaseSharingView
from plone.dexterity.interfaces import IDexterityFTI
from plone.uuid.interfaces import IUUID
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
import mimetypes
import json


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
        result = self.process_request()
        if self.request.get_header('HTTP_ACCEPT') == 'application/json':
            self.request.response.setHeader("Content-type", "application/json")
            return json.dumps(result)
        else:
            self.request.response.redirect(self.context.absolute_url())

    def process_request(self):
        # XXX: We don't support the TUS resumable file upload protocol.
        # The pat-upload pattern supports it (due to mockup) and
        # plone.app.content.browser.file.py also supports it, but at the cost
        # of not being able to upload multiple files at once. We decided that
        # that's more important at the moment.
        if self.request.REQUEST_METHOD != 'POST':
            return []
        result = []
        form = self.request.form
        for name in [k for k in form.keys() if k.startswith('file')]:
            output = self.create_file_from_request(name)
            if output:
                result.append(output)
        return result

    def create_file_from_request(self, name):
        context = self.context
        filedata = self.request.form.get(name, None)
        if not filedata:
            return
        filename = filedata.filename
        content_type = mimetypes.guess_type(filename)[0] or ""
        # Determine if the default file/image types are DX or AT based
        ctr = api.portal.get_tool('content_type_registry')
        type_ = ctr.findTypeName(filename.lower(), '', '') or 'File'
        pt = api.portal.get_tool('portal_types')

        if IDexterityFTI.providedBy(getattr(pt, type_)):
            obj = IDXFileFactory(context)(filename, content_type, filedata)
            if hasattr(obj, 'file'):
                size = obj.file.getSize()
                content_type = obj.file.contentType
            elif hasattr(obj, 'image'):
                size = obj.image.getSize()
                content_type = obj.image.contentType
            else:
                return
            result = {
                "type": content_type,
                "size": size
            }
        else:
            from Products.ATContentTypes.interfaces import IATCTFileFactory
            obj = IATCTFileFactory(context)(filename, content_type, filedata)
            try:
                size = obj.getSize()
            except AttributeError:
                size = obj.getObjSize()
            result = {
                "type": obj.getContentType(),
                "size": size
            }
        result.update({
            'url': obj.absolute_url(),
            'name': obj.getId(),
            'UID': IUUID(obj),
            'filename': filename
        })
        return result
