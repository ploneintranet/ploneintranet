# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from ploneintranet.layout.interfaces import IModalPanel
from Products.Five import BrowserView
from zope.interface import implementer


class BaseView(BrowserView):
    ''' Base view that knows when it is called through ajax
    and if diazo should be disabled
    '''

    @memoize_contextless
    def is_posting(self):
        ''' Check if we the user is posting
        '''
        return self.request.method == 'POST'

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

    def redirect(self, target=None, msg='', msg_type='warning'):
        '''
        '''
        if msg:
            api.portal.show_message(msg, self.request, msg_type)
        if not target:
            target = self.context
        if not isinstance(target, basestring):
            context_state = api.content.get_view(
                'plone_context_state',
                target,
                self.request,
            )
            target = context_state.view_url()
        return self.request.response.redirect(target)

    def __call__(self):
        ''' Check if we can bookmark and render the template
        '''
        self.maybe_disable_diazo()
        return super(BaseView, self).__call__()


@implementer(IModalPanel)
class BasePanel(BaseView):
    ''' Inherit from this if you want to create a modal panel
    '''
    is_modal_panel = True
    show_default_cancel_button = True
    form_method = 'post'
    _form_data_pat_inject_parts = (
        '#global-statusmessage; loading-class: \'\'',
        '#document-content',
    )

    @property
    @memoize
    def form_action(self):
        ''' The handler for this form
        '''
        return '{url}/@@{action}'.format(
            url=self.context.absolute_url(),
            action=self.__name__,
        )

    @property
    @memoize
    def form_data_pat_inject(self):
        ''' Merge the data inject parts to populate
        the form data-pat-inject attribute
        '''
        return ' && '.join(self._form_data_pat_inject_parts)
