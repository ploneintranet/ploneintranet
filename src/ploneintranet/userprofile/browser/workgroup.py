# coding=utf-8
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from Products.Five import BrowserView
from zope.interface import implements
from ZTUtils import make_query


class WorkGroupView(BrowserView):
    implements(IBlocksTransformEnabled)
    """View for user profile."""

    my_groups = my_workspaces = []

    _default_tabs = (
        u'group-view',
    )

    # I suggest a multiple of 6
    _batch_size = 12
    userprofile_portal_types = (
        'ploneintranet.userprofile.userprofile',
    )

    def page_number(self):
        '''Get current page number from the request'''
        try:
            page = int(self.request.form.get('page', 1))
        except ValueError:
            page = 1
        return page

    def get_start(self):
        '''
        Fills the start parameter of the search query,
        i.e. the first element of the batch
        '''
        return (self.page_number() - 1) * self._batch_size

    def next_page_number(self):
        '''Get page number for next page of search results'''
        page = self.page_number()
        item_length = len(self.brains)
        if page * self._batch_size < item_length:
            return page + 1
        else:
            return None

    def next_page_url(self):
        '''Get url for the next page of results'''
        next_page_number = self.next_page_number()
        if not next_page_number:
            return ''
        new_query = make_query(
            self.request.form.copy(),
            {'page': next_page_number}
        )
        return '{url}?{qs}'.format(
            url=self.request.ACTUAL_URL,
            qs=new_query
        )

    @property
    @memoize
    def brains(self):
        '''Return the brains of the users we are searching for
        '''
        userids = self.userids
        if not userids:
            return []
        pc = api.portal.get_tool('portal_catalog')
        return pc.unrestrictedSearchResults(
            getId=userids,
            portal_type=self.userprofile_portal_types,
            sort_on='sortable_title',
        )

    def batch(self):
        '''
        '''
        brains = self.brains
        start = self.get_start()
        if start >= len(brains):
            return []
        end = start + self._batch_size
        return brains[start:end]

    @property
    @memoize
    def groups_container(self):
        ''' Returns the group container (if found) or an empty dictionary
        '''
        portal = api.portal.get()
        return portal.get('groups', {})

    @property
    @memoize
    def users_container(self):
        ''' Returns the group container (if found) or an empty dictionary
        '''
        portal = api.portal.get()
        return portal.get('profiles', {})

    @property
    @memoize
    def userids(self):
        ''' Return the member ids that are in the user profile container
        '''
        container = self.users_container
        return [
            key for key in self.context.members
            if key in container
        ]

    @property
    @memoize
    def users(self):
        ''' Return the user that are in the user profile container
        '''
        container = self.users_container
        keys = self.userids
        return [container[key] for key in keys]

    @property
    @memoize
    def groupids(self):
        ''' Return the group ids that are in the group container
        '''
        container = self.groups_container
        return [
            key for key in self.context.members
            if key in container
        ]

    @property
    @memoize
    def groups(self):
        ''' Return the groups that are in the group container
        '''
        container = self.groups_container
        keys = self.groupids
        return [container[key] for key in keys]

    def get_avatar_tag(self, userid):
        ''' Provide HTML tag to display the avatar
        '''
        return pi_api.userprofile.avatar_tag(
            username=userid
        )
