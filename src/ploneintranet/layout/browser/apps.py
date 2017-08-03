# coding=utf-8
from AccessControl.unauthorized import Unauthorized
from datetime import datetime
from logging import getLogger
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.app import IApp
from ploneintranet.layout.browser.base import BasePanel
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from zope.interface import implementer
from zope.publisher.browser import BrowserView

import json


logger = getLogger(__name__)


class AppNotAvailable(BasePanel):

    """ A nice not available page to be able to demo this beautifully
    """
    title = _('App not available')
    form_action = ''
    panel_size = 'small'
    show_default_cancel_button = False


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

    def condition(self):
        ''' A tal condition that controls if this tile should be rendered
        '''
        if self.context.condition:
            expr_context = createExprContext(
                self.context, api.portal.get(), self.context)
            expr = Expression(self.context.condition)
            return bool(expr(expr_context))
        else:
            return True

    @property
    @memoize
    def modal(self):
        ''' Open in a modal returning 'pat-modal'.
        If you want, instead to follow the click just return ''
        '''
        if self.not_found or self.unauthorized:
            return 'pat-modal'
        return ''

    @property
    @memoize
    def inject(self):
        ''' Check if we should inject this tile
        '''
        if self.modal:
            return ''
        # XXX Get rid of the check for "@@external-app" and migrate to the
        # "external" field
        if self.context.external or self.context.app == '@@external-app':
            return ''
        return 'pat-inject pat-switch'

    @property
    @memoize
    def pat_inject_options(self):
        ''' Check if we should inject this tile
        '''
        if not self.inject:
            return
        if self.modal:
            return '#document-content'
        return '#app-space; history: record;'

    @property
    @memoize
    def url(self):
        ''' Return the url will be addressed to when clicking this tile
        '''
        if self.modal:
            template = '{url}/@@{view}#document-content'
            url = api.portal.get().absolute_url()
            if self.not_found:
                view = 'app-not-available.html'
            else:
                view = 'app-unauthorized'
            return template.format(
                url=url,
                view=view,
            )
        return self.context.app_url()

    def get_class(self):
        return self.context.css_class or self.context.getId()


class AppNoBarcelonetaView(AppTile):
    ''' Redirect the user to the proper location
    when he tries to visit the app object in Quaive
    '''
    def __call__(self):
        return self.request.response.redirect(self.url)


class AppRedirect(BrowserView):
    """Redirect to a URL specified in the app_parameters"""

    def __call__(self):
        url = json.loads(self.context.app_parameters).get('url')
        return self.request.response.redirect(url)
