# coding=utf-8
from Acquisition import aq_inner
from plone.memoize.view import memoize
from plone.protect.authenticator import createToken
from Products.Five import BrowserView
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from urllib import urlencode
from AccessControl import Unauthorized
from plone import api
from zope.interface import Interface
from zope.interface import implements
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class IPinned(Interface):
    """ Marker Interface to state if an object is pinned """


# Adapter to override in final implementation

class IPinner(Interface):
    """ Provides methods to manage an objects pinning """

    def is_pinned(self):
        """ determine if an object is pinned in its workspace

        @return: True or False
        """

    def pin(self):
        """ pin an object if not yet pinned
        """

    def unpin(self):
        """ unpin an object if pinned
        """


class Pinner(object):
    """ Adapt object to find out if it is pinned and manage pinning
        Simple implementation which only uses marker interface
    """

    implements(IPinner)

    def __init__(self, context):
        self.context = context

    def is_pinned(self):
        """ Return bool if pinned. Register a better one
        """
        return IPinned.providedBy(aq_inner(self.context))

    def pin(self):
        if not self.is_pinned():
            alsoProvides(aq_inner(self.context), IPinned)

    def unpin(self):
        if self.is_pinned():
            noLongerProvides(aq_inner(self.context), IPinned)


# View classes to handle UI

class View(BrowserView):
    ''' PRELIMINARY! This is only partial. Pinning may come later.

    A view that pins the context to the workspace
    A context can be a Plone object or a search result
    '''
    base_css_class = 'icon-pin pin'

    @property
    def available(self):
        return True

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
    def is_pinned(self):
        ''' Check if an object is pinned
        '''
        return IPinner(self.context).is_pinned()

    @property
    def link_options(self):
        ''' Get the link options
        '''
        if self.is_pinned:
            options = {
                'action': '@@unpin',
                'title': _('Unpin this item from the workspace'),
                'css_class': 'checked',
                'label': _('Unpinned'),
            }
        else:
            options = {
                'action': '@@pin',
                'title': _('Pin this item to the workspace'),
                'css_class': 'unchecked',
                'label': _('Pinned'),
            }
        try:
            options['base_url'] = self.context.absolute_url()
        except AttributeError:
            options['base_url'] = self.context.url
        return options


class ViewIconified(View):
    ''' Iconified version of view
    '''
    base_css_class = 'iconified icon-pin pin'

    @property
    def link_options(self):
        ''' Get the link options
        '''
        options = super(ViewIconified, self).link_options
        if self.is_pinned:
            options['label'] = _('Unpin')
        return options


class PinningBaseView(ViewIconified):

    @memoize
    def is_ajax(self):
        ''' Check if we have an ajax call
        '''
        requested_with = self.request.environ.get('HTTP_X_REQUESTED_WITH')
        return requested_with == 'XMLHttpRequest'

    def disable_diazo(self):
        ''' Disable diazo if this is an ajax call
        '''
        self.request.response.setHeader('X-Theme-Disabled', '1')

    def __call__(self):
        ''' Check if we can pin and render the template
        '''
        if self.is_ajax():
            self.disable_diazo()
        self.action()
        return super(PinningBaseView, self).__call__()


class UnpinView(PinningBaseView):
    ''' The view for unpinning content
    '''
    def action(self):
        ''' Check if we can unpin this
        '''
        if api.user.is_anonymous():
            raise Unauthorized

        IPinner(self.context).unpin()


class PinView(PinningBaseView):
    ''' The view for pinning content
    '''
    def action(self):
        ''' Check if we can pin this
        '''
        if api.user.is_anonymous():
            raise Unauthorized
        IPinner(self.context).pin()
