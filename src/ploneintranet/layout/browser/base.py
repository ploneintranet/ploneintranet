# coding=utf-8
from plone.memoize.view import memoize_contextless
from Products.Five import BrowserView


class BaseView(BrowserView):
    ''' Base view that knows when it is called through ajax
    and if diazo should be disabled
    '''
    @memoize_contextless
    def is_ajax(self):
        ''' Check if we have an ajax call
        '''
        requested_with = self.request.environ.get('HTTP_X_REQUESTED_WITH')
        return requested_with == 'XMLHttpRequest'

    def maybe_disable_diazo(self):
        ''' Disable diazo if needed
        '''
        if self.is_ajax():
            self.request.response.setHeader('X-Theme-Disabled', '1')

    def __call__(self):
        ''' Check if we can bookmark and render the template
        '''
        self.maybe_disable_diazo()
        return super(BaseView, self).__call__()
