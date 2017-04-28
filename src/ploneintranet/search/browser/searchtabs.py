# coding=utf-8
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.Five import BrowserView
from urllib import urlencode


class View(BrowserView):

    _tabs = [
        {
            'view': 'search',
            'title': _('All'),
        },
        {
            'view': 'search_people',
            'title': _('People'),
        },
        {
            'view': 'search_images',
            'title': _('Images'),
        },
        {
            'view': 'search_files',
            'title': _('Files'),
        },
    ]

    def get_tabs(self):
        ''' Return the list of tabs
        '''
        params = {'SearchableText': self.request.get('SearchableText', '')}
        url_template = ''.join((
            self.context.absolute_url(),
            '/@@{view}'
            '?',
            urlencode(params),
            '#results'
        ))
        current_view = self.request.steps[-1].lstrip('@@')
        for tab in self._tabs:
            tab = tab.copy()
            tab['url'] = url_template.format(**tab)
            if tab['view'] == current_view:
                tab['extra_class'] = 'current'
            yield tab
