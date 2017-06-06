# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_inner
from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.app.content.browser.file import FileUploadView as BaseFileUploadView
from plone.app.dexterity.factories import upload_lock
from plone.app.layout.viewlets.content import ContentHistoryView as BaseContentHistoryView  # noqa
from plone.app.workflow.browser.sharing import SharingView as BaseSharingView
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.memoize.view import memoize
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.protect.authenticator import createToken
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.uuid.interfaces import IUUID
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.config import INTRANET_USERS_GROUP_ID
from ploneintranet.workspace.subscribers import _update_workspace_groupings
from Products.CMFCore.utils import _checkPermission
from Products.CMFEditions.Permissions import AccessPreviousVersions
from Products.CMFPlone import utils as ploneutils
from Products.Five.browser import BrowserView
from urllib import urlencode
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent

import json
import mimetypes
import transaction


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
        results = super(SharingView, self).role_settings()
        uid = self.context.UID()
        # We do not want to share to the current context,
        # to authenticated users
        # and to all intranet users
        return [
            result for result in results
            if not (
                result["id"].endswith(uid) or
                result["id"] in ("AuthenticatedUsers", INTRANET_USERS_GROUP_ID)
            )
        ]

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

    @property
    @memoize
    def groupname(self):
        ''' Return the groupname
        '''
        groupname = self.request.get('groupname')
        if groupname and groupname != 'Untagged':
            return groupname

    def __call__(self):
        result = self.process_request()
        if self.request.get_header('HTTP_ACCEPT') == 'application/json':
            self.request.response.setHeader("Content-type", "application/json")
            return json.dumps(result)
        target = self.context.absolute_url() + '/@@sidebar.documents'
        groupname = self.groupname
        if groupname:
            target = '{url}?{qs}'.format(
                url=target,
                qs=urlencode({
                    'groupname': groupname,
                })
            )
        self.request.response.redirect(target)

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

    def post_factory(self, obj):
        ''' Things to do after the object has been created in this form
        '''
        groupname = self.groupname
        if groupname:
            obj.setSubject(groupname)
            _update_workspace_groupings(obj, None)

    def set_filedata(self, obj, filedata, filename, content_type):
        ''' Try to understand what is the primary field
        and store the data there
        '''
        try:
            info = IPrimaryFieldInfo(obj, None)
        except TypeError:
            info = None
        fieldname = info and info.fieldname or 'file'
        # This should take care of File and images
        if 'image' in fieldname:
            blob_factory = NamedBlobImage
        else:
            blob_factory = NamedBlobFile
        filename = ploneutils.safe_unicode(filename)
        value = blob_factory(
            data=filedata,
            filename=filename,
            contentType=content_type
        )
        return setattr(obj, fieldname, value)

    def create_dx_file(self, filename, content_type, filedata, portal_type):
        ''' Inspired by plone.app.dexterity.factories.IDXFileFactory
        '''
        name = filename.decode('utf8')
        chooser = INameChooser(self.context)
        # otherwise I get ZPublisher.Conflict ConflictErrors
        # when uploading multiple files
        upload_lock.acquire()
        newid = chooser.chooseName(name, self.context.aq_parent)
        try:
            obj = createContentInContainer(
                self.context,
                portal_type,
                id=newid,
            )
            self.set_filedata(obj, filedata, name, content_type)
            obj.title = name
            obj.reindexObject()
            transaction.commit()
        finally:
            upload_lock.release()
        return obj

    def create_file_from_request(self, name):
        context = self.context
        filedata = self.request.form.get(name, None)
        if not filedata:
            return
        filename = filedata.filename
        content_type = mimetypes.guess_type(filename)[0] or ""
        # Determine if the default file/image types are DX or AT based
        ctr = api.portal.get_tool('content_type_registry')
        type_ = ctr.findTypeName(filename.lower(), content_type, '')

        if not type_ == 'Image':
            type_ = 'File'

        pt = api.portal.get_tool('portal_types')

        if IDexterityFTI.providedBy(getattr(pt, type_)):
            obj = self.create_dx_file(filename, content_type, filedata, type_)
            self.post_factory(obj)
            notify(ObjectCreatedEvent(obj))
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
            self.post_factory(obj)
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


class ContentHistoryView(BaseContentHistoryView):
    """
        Customised so that we can provide more info about the revisions in our
        history.
    """

    def revisionHistory(self):
        context = aq_inner(self.context)
        if not _checkPermission(AccessPreviousVersions, context):
            return []

        rt = api.portal.get_tool("portal_repository")
        if rt is None or not rt.isVersionable(context):
            return []

        context_url = context.absolute_url()
        history = rt.getHistoryMetadata(context)

        # XXX Hardcoded: diff is not supported
        can_diff = False
        can_revert = _checkPermission(
            'CMFEditions: Revert to previous versions', context)

        def morphVersionDataToHistoryFormat(vdict, version_id):
            meta = vdict["metadata"]["sys_metadata"]
            userid = meta["principal"]
            token = createToken()
            # XXX For Files, link to the download view
            if context.portal_type in ('File',):
                preview_url = "{0}/download_file_version?version_id={1}&_authenticator={2}".format(  # noqa
                    context_url, version_id, token)
            else:
                preview_url = \
                    "%s/versions_history_form?version_id=%s&_authenticator=%s#version_preview" % (  # noqa
                        context_url,
                        version_id,
                        token
                    )
            info = dict(
                type='versioning',
                action=_(u"Edited"),
                transition_title=_(u"Edited"),
                actorid=userid,
                time=meta["timestamp"],
                comments=meta['comment'],
                version_id=version_id,
                preview_url=preview_url,
            )
            up_to_date = rt.isUpToDate(context, version_id)
            if can_diff:
                if version_id > 0:
                    info["diff_previous_url"] = (
                        "%s/@@history?one=%s&two=%s&_authenticator=%s" %
                        (context_url, version_id, version_id - 1, token)
                    )
                if not up_to_date:
                    info["diff_current_url"] = (
                        "%s/@@history?one=current&two=%s&_authenticator=%s" %
                        (context_url, version_id, token)
                    )
            if can_revert and not up_to_date:
                info["revert_url"] = "%s/revertversion" % context_url
            else:
                info["revert_url"] = None
            info.update(self.getUserInfo(userid))
            return info

        # History may be an empty list
        if not history:
            return history

        version_history = []
        # Count backwards from most recent to least recent
        for i in xrange(history.getLength(countPurged=False) - 1, -1, -1):
            vdict = history.retrieve(i, countPurged=False)
            version_id = history.getVersionId(i, countPurged=False)
            morphed_data = morphVersionDataToHistoryFormat(
                vdict, version_id)
            version_history.append(morphed_data)

        return version_history
