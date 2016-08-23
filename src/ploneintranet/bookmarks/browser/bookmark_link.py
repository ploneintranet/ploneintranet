# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from plone.protect.authenticator import createToken
from ploneintranet.bookmarks.browser.base import BookmarkView
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from urllib import urlencode


class View(BookmarkView):
    ''' A view that outputs a bookmark link on this context

    A context can be a Plone object or a search result
    '''
    base_css_class = 'icon pat-inject'

    @property
    def query_options(self):
        ''' The query string options for the bookmark action
        '''
        options = {
            '_authenticator': createToken(),
        }
        return options

    @property
    def query_string(self):
        ''' The urlencoded query string options for the bookmark action
        '''
        return urlencode(self.query_options)

    @property
    @memoize
    def is_bookmarked(self):
        ''' Check if an object is bookmarked by uid
        '''
        uid = self.context.UID
        if uid is None:
            uid = self.context.context.UID
        if callable(uid):
            uid = uid()
        return self.ploneintranet_network.is_bookmarked('content', uid)

    @property
    def link_options(self):
        ''' Get the link options
        '''
        if self.is_bookmarked:
            options = {
                'action': '@@unbookmark',
                'title': _('Remove this item from your bookmarks'),
                'css_class': 'icon-bookmark active ',
                'label': _('Remove bookmark'),
            }
        else:
            options = {
                'action': '@@bookmark',
                'title': _('Add this item to your bookmarks'),
                'css_class': 'icon-bookmark-empty',
                'label': _('Bookmark'),
            }

        try:
            options['base_url'] = self.context.absolute_url()
        except AttributeError:
            options['base_url'] = self.context.url

        return options


class ViewIconified(View):
    ''' Iconified version of view
    '''
    base_css_class = 'icon iconified pat-inject'

    @property
    def link_options(self):
        ''' Get the link options
        '''
        options = super(ViewIconified, self).link_options
        if self.is_bookmarked:
            options['label'] = _('Remove bookmark')
        return options

    @property
    def query_options(self):
        ''' Add iconified=True
        '''
        options = super(ViewIconified, self).query_options
        options['iconified'] = True
        return options


class AppViewIconified(ViewIconified):
    ''' The icon that will work for applications
    '''
    @property
    @memoize
    def is_bookmarked(self):
        ''' Check if an object is bookmarked by uid
        '''
        return self.ploneintranet_network.is_bookmarked(
            'apps',
            self.context.path,
        )

    @property
    def query_options(self):
        ''' Add iconified=True
        '''
        options = super(AppViewIconified, self).query_options
        options['app'] = self.context.path
        return options

    @property
    def link_options(self):
        ''' Get the link options
        '''
        options = super(AppViewIconified, self).link_options
        if self.is_bookmarked:
            options['action'] = '@@unbookmark-app'
        else:
            options['action'] = '@@bookmark-app'
        options['base_url'] = api.portal.get().absolute_url()
        return options
