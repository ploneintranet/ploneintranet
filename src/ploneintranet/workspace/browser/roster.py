from itertools import chain
from plone import api
from plone.memoize.instance import memoize
from zope.i18n import translate
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zExceptions import Forbidden

from collective.workspace.interfaces import IWorkspace
from ploneintranet.workspace import MessageFactory as _


def merge_search_results(results, key):
    """Merge member search results.

    Based on PlonePAS.browser.search.PASSearchView.merge.
    """
    output = {}
    for entry in results:
        id = entry[key]
        if id not in output:
            output[id] = entry.copy()
        else:
            buf = entry.copy()
            buf.update(output[id])
            output[id] = buf

    return output.values()


class EditRoster(BrowserView):

    index = ViewPageTemplateFile('roster-edit.pt')

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        postback = self.handle_form()
        if postback:
            return self.index()
        else:
            url = '%s/team-roster' % self.context.absolute_url()
            self.request.response.redirect(url)

    def handle_form(self):
        """
        We split this out so we can reuse this for ajax.
        Will return a boolean if it was a post or not
        """
        postback = True

        form = self.request.form
        submitted = form.get('form.submitted', False)
        save_button = form.get('form.button.Save', None) is not None
        cancel_button = form.get('form.button.Cancel', None) is not None
        if submitted and save_button and not cancel_button:
            if not self.request.get('REQUEST_METHOD', 'GET') == 'POST':
                raise Forbidden

            authenticator = self.context.restrictedTraverse('@@authenticator',
                                                            None)
            if not authenticator.verify():
                raise Forbidden

            # Update settings for users and groups
            entries = form.get('entries', [])
            settings = []
            for entry in entries:
                settings.append(
                    dict(
                        id=entry['id'],
                        member=entry.get('update') == '1',
                    )
                )
            if settings:
                self.update_users(settings)
            # IStatusMessage(self.request).addStatusMessage(
            #     _(u"Changes saved."), type='info')

        # Other buttons return to the sharing page
        if cancel_button:
            postback = False

        return postback

    def update_users(self, settings):
        ws = IWorkspace(self.context)
        members = ws.members

        for setting in settings:

            id = setting['id']
            is_member = setting['member']

            # Existing members, no-longer selected
            if id in members and not is_member:
                member = members[id]
                # Don't remove them if they're an Admin
                if 'Admins' not in member['groups']:
                    ws.membership_factory(ws, member).remove_from_team()

            # New members
            if id not in members and is_member:
                ws.add_to_team(user=id)

    def users(self):
        """Get current users.

        Returns a list of dicts with keys:

         - id
         - title
        """
        existing_users = self.existing_users()
        user_results = self.user_search_results()

        current_users = existing_users + user_results

        current_users.sort(key=lambda x: safe_unicode(x["title"]))
        return current_users

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
                    disabled='Admins' in details['groups'],
                )
            )

        return info

    def _principal_search_results(self,
                                  search_for_principal,
                                  get_principal_by_id,
                                  get_principal_title,
                                  id_key):
        """Return search results for a query to add new users or groups.

        Returns a list of dicts, as per role_settings().

        Arguments:
            search_for_principal -- a function that takes an IPASSearchView and
                a search string. Uses the former to search for the latter and
                returns the results.
            get_principal_by_id -- a function that takes a user id and returns
                the user of that id
            get_principal_title -- a function that takes a user and a default
                title and returns a human-readable title for the user. If it
                can't think of anything good, returns the default title.
            principal_type -- either 'user' or 'group', depending on what kind
                of principals you want
            id_key -- the key under which the principal id is stored in the
                dicts returned from search_for_principal
        """
        context = self.context

        translated_message = translate(
            _(u"Search for user or group"),
            context=self.request)
        search_term = self.request.form.get('search_term', None)
        if not search_term or search_term == translated_message:
            return []

        existing_users = set([p['id'] for p in self.existing_users()])

        info = []

        hunter = getMultiAdapter((context, self.request), name='pas_search')
        for principal_info in search_for_principal(hunter, search_term):
            principal_id = principal_info[id_key]
            if principal_id not in existing_users:
                principal = get_principal_by_id(principal_id)
                if principal is None:
                    continue

                info.append(
                    dict(
                        id=principal_id,
                        title=get_principal_title(principal, principal_id),
                        disabled=False,
                        member=False,
                    ))
        return info

    def user_search_results(self):
        """Return search results for a query to add new users.

        Returns a list of dicts, as per role_settings().
        """

        def search_for_principal(hunter, search_term):
            return merge_search_results(
                chain(*[hunter.searchUsers(**{field: search_term})
                      for field in ['name', 'fullname', 'email']]), 'userid')

        def get_principal_by_id(user_id):
            acl_users = getToolByName(self.context, 'acl_users')
            return acl_users.getUserById(user_id)

        def get_principal_title(user, default):
            return user.getProperty('fullname') or user.getId() or default

        return self._principal_search_results(
            search_for_principal,
            get_principal_by_id, get_principal_title, 'userid')
