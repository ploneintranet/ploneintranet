from itertools import chain
from plone import api
from plone.memoize.instance import memoize, clearafter
from zope.i18n import translate
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.app.workflow.browser.sharing import SharingView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.protect import CheckAuthenticator, PostOnly
from Products.Five import BrowserView

from zExceptions import Forbidden

from collective.workspace.interfaces import IWorkspace
from ploneintranet.workspace import MessageFactory as _


class EditRoster(BrowserView):
    """Roster management page.

    Based on the @@sharing tab from plone.app.workflow
    """

    index = ViewPageTemplateFile('roster-edit.pt')

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        self.handle_form()
        return self.index()

    def handle_form(self):
        form = self.request.form
        submitted = form.get('form.submitted', False)
        save_button = form.get('form.button.Save', None) is not None
        if submitted and save_button:
            CheckAuthenticator(self.request)
            PostOnly(self.request)
            entries = form.get('entries', [])
            self.update_users(entries)

    @clearafter
    def update_users(self, entries):
        """Update user properties on the roster """
        ws = IWorkspace(self.context)
        members = ws.members

        for entry in entries:

            id = entry['id']
            is_member = bool(entry.get('member'))
            is_admin = bool(entry.get('admin'))

            # Existing members
            if id in members:
                member = members[id]
                if not is_member:
                    ws.membership_factory(ws, member).remove_from_team()
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
        """Get current users.

        Returns a list of dicts with keys:

         - id
         - title
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

    @memoize
    def existing_users(self):
        members = IWorkspace(self.context).members
        info = []
        for userid, details in members.items():
            user = api.user.get(userid).getUser()
            title = user.getProperty('fullname') or user.getId() or userid
            info.append(
                dict(
                    id=userid,
                    title=title,
                    member=True,
                    admin='Admins' in details['groups'],
                )
            )

        return info
