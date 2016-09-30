# coding=utf-8
from datetime import datetime
from AccessControl.unauthorized import Unauthorized
from logging import getLogger
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.view import memoize
from zope.interface import implementer
from zope.publisher.browser import BrowserView

from ploneintranet.layout.app import IApp

logger = getLogger(__name__)


class AppNotAvailable(BrowserView):

    """ A nice not available page to be able to demo this beautifully
    """


class Apps(BrowserView):

    """ A view to serve as overview over apps
    """

    def apps(self):
        """ list available apps, to be rendered as tiles
        """
        catalog = api.portal.get_tool('portal_catalog')
        query = dict(object_provides=IApp.__identifier__)
        items = [x.getObject() for x in catalog(query)]
        items.sort(key=lambda x: x.Title())
        return items


@implementer(IBlocksTransformEnabled)
class AppTile(BrowserView):

    @property
    @memoize
    def app_view(self):
        return self.context.app_view(self.request)

    @property
    @memoize
    def counter(self):
        ''' Show a counter if needed
        '''
        if self.disabled:
            return
        return getattr(self.app_view, 'counter', None)

    @property
    @memoize
    def date(self):
        ''' Show a date if needed (e.g. Calendar)
        '''
        return datetime.now()

    @property
    @memoize
    def digits(self):
        ''' Show a counter if needed
        '''
        return len(str(self.counter or ''))

    @property
    @memoize
    def can_view_context(self):
        return api.user.has_permission('View', obj=self.context)

    @property
    @memoize
    def unauthorized(self):
        ''' Check if we are authorized to view this app

        - the app should be there
        - the app contenxt should be viewable
        - the view of the app should be viewable
        '''
        if self.not_found:
            # this will be the same error that restrictedTraverse will raise
            raise AttributeError('Path not found')
        if not self.can_view_context:
            return True
        try:
            self.context.restrictedTraverse(self.context.app)
        except Unauthorized:
            return True
        return False

    @property
    @memoize
    def not_found(self):
        ''' Check if the url actually exists and is meaningful
        '''
        if not self.context.app:
            return True
        target = self.context.unrestrictedTraverse(self.context.app, None)
        if target is None:
            return True
        return False

    @property
    @memoize
    def disabled(self):
        ''' Check if the user has the rights to traverse to the existing path
        '''
        if not self.context.app:
            return 'disabled'
        if self.not_found:
            return 'disabled'
        if self.unauthorized:
            return 'disabled'
        return ''

    @property
    def modal(self):
        ''' Open in a modal returning 'pat-modal'.
        If you want, instead to follow the ling just return ''
        '''
        if self.not_found:
            return 'pat-modal'
        return ''

    def get_class(self):
        return self.context.css_class or self.context.getId()
