from AccessControl import Unauthorized
from Products.CMFCore.utils import _checkPermission as checkPermission
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.workspace.interfaces import IWorkspace
from plone import api
from plone.memoize.instance import clearafter
from plone.protect import CheckAuthenticator, PostOnly
from ploneintranet.workspace import MessageFactory as _
from zope.component import getMultiAdapter
from ploneintranet.workspace.browser.workspace import BaseWorkspaceView
from ploneintranet.workspace.utils import existing_users


class EditRoster(BaseWorkspaceView):
    """Roster management page.

    Based on the @@sharing tab from plone.app.workflow
    """

    index = ViewPageTemplateFile('templates/roster-edit.pt')

    def __call__(self):
        return self.index()

    def update_roster(self, REQUEST=None):
        """
        If workspace is team managed, users can add/remove participants.
        Any user with the manage workspace permission can add/remove
        participants and admins.
        """
        CheckAuthenticator(self.request)
        PostOnly(self.request)
        form = self.request.form
        entries = form.get('entries', [])
        self.update_users(entries)
        api.portal.show_message(message=_(u'Roster updated.'),
                                request=self.request)
        return self.request.response.redirect(
            '%s/@@edit-roster' % self.context.absolute_url())

    @clearafter
    def update_users(self, entries):
        """Update user properties on the roster """
        ws = IWorkspace(self.context)
        members = ws.members

        # check user permissions against join policy
        join_policy = self.context.join_policy
        if (join_policy == "admin"
            and not checkPermission(
                "collective.workspace: Manage roster",
                self.context)):
            raise Unauthorized("You are not allowed to add users here")

        for entry in entries:
            id = entry.get('id')
            is_member = bool(entry.get('member'))
            is_admin = bool(entry.get('admin'))

            # Existing members
            if id in members:
                member = members[id]
                if not is_member:
                    if checkPermission(
                            "ploneintranet.workspace: Manage workspace",
                            self.context):
                        ws.membership_factory(ws, member).remove_from_team()
                    else:
                        raise Unauthorized(
                            "Only team managers can remove members")
                elif not is_admin:
                    ws.membership_factory(ws, member).groups -= {'Admins'}
                else:
                    ws.membership_factory(ws, member).groups |= {'Admins'}

            # New members
            elif id not in members and (is_member or is_admin):
                groups = set()
                if is_admin:
                    groups.add('Admins')
                ws.add_to_team(user=id, groups=groups)

    def users(self):
        """Get current users and add in any search results.

        :returns: a list of dicts with keys
         - id
         - title
        :rtype: list
        """
        existing_users = self.existing_users()
        existing_user_ids = [x['id'] for x in existing_users]

        # Only add search results that are not already members
        sharing = getMultiAdapter((self.context, self.request),
                                  name='sharing')
        search_results = sharing.user_search_results()
        users = existing_users + [x for x in search_results
                                  if x['id'] not in existing_user_ids]

        users.sort(key=lambda x: safe_unicode(x["title"]))
        return users

    def existing_users(self):
        return existing_users(self.context)

    def can_manage_workspace(self):
        """
        does this user have permission to manage the workspace
        """
        return checkPermission(
            "ploneintranet.workspace: Manage workspace",
            self.context,
        )

    def can_add_users(self):
        """
        admins can add users.
        if the workspace is team or self managed then members can
        add other users too.
        """
        if self.can_manage_workspace():
            return True

        return self.context.join_policy in {'self', 'team'}

    def admin_managed_workspace(self):
        """
        is this workspace admin managed?
        """
        return self.context.join_policy == 'admin'
