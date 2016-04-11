# -*- encoding: utf-8 -*-
from datetime import datetime
from plone import api
from plone import api as plone_api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.textfield.value import RichTextValue
from plone.memoize import forever
from plone.memoize.view import memoize
from ploneintranet.search.interfaces import ISiteSearch
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from zope.component import getUtility
from ZTUtils import make_query


class SearchResultsView(BrowserView):

    # Map portal types to url fragments so that the correct sidebar
    # section is opened
    url_fragments = {
        u'Document': '#workspace-documents',
        u'Image': '#workspace-documents',
        u'File': '#workspace-documents',
        u'todo': '#workspace-tickets',
        u'Event': '#workspace-events',
    }

    _default_preview_class = 'file'
    _preview_class_mapping = {
        'user': (
            'ploneintranet.userprofile.userprofile',
        ),
        'rich': (
            'Document',
            'News Item',
        ),
        'event': (
            'Event',
        ),
        'workspace': (
            'ploneintranet.workspace.case',
            'ploneintranet.workspace.workspacefolder',
        ),
        'file': (
            'ploneintranet.userprofile.userprofilecontainer',
            'todo',
            'Folder',
            'File',
            'Image',
        )
    }

    _facet_fallback_type_class = 'type-file'
    _batch_size = 10

    def _extract_date(self, field):
        ''' Convert the string passed by pat-date-picker
        in to a datetime object
        '''
        try:
            return datetime.strptime(
                self.request.form.get(field, ''),
                '%Y-%m-%d'
            )
        except ValueError:
            return

    def page_number(self):
        """Get current page number from the request"""
        try:
            page = int(self.request.form.get('page', 1))
        except ValueError:
            page = 1
        return page

    def get_start(self):
        """
        Fills the start parameter of the search query,
        i.e. the first element of the batch
        """
        return (self.page_number() - 1) * self._batch_size

    def next_page_number(self, total_results):
        """Get page number for next page of search results"""
        page = self.page_number()
        if page * self._batch_size < total_results:
            return page + 1
        else:
            return None

    def next_page_url(self, total_results):
        """Get url for the next page of results"""
        next_page_number = self.next_page_number(total_results)
        if not next_page_number:
            return
        new_query = make_query(
            self.request.form.copy(),
            {'page': next_page_number}
        )
        return '{url}?{qs}'.format(
            url=self.request.ACTUAL_URL,
            qs=new_query
        )

    def friendly_path(self, url):
        """Show the object path within the navigation root"""
        root_url = api.portal.get_navigation_root(self.context).absolute_url()
        return url.replace(root_url, '')

    @forever.memoize
    def preview_class(self, portal_type):
        """Get the matching preview class according to portal type.

        If found on the mapping repurn the key, otherwise return a default.
        """
        for key in self._preview_class_mapping:
            if portal_type in self._preview_class_mapping[key]:
                return key
        return self._default_preview_class

    def get_text_preview(self, result):
        ''' Given a search result return a preview
        '''
        obj = result.getObject()
        text = getattr(obj, 'text', None)
        if isinstance(text, RichTextValue):
            return text.raw
        return text or u''

    def search_options(self):
        """Get the currently options for refining results.

        These are generated from all fields registered as
        *both* a facet field and a filter field
        """
        filter_names = set(plone_api.portal.get_registry_record(
            'ploneintranet.search.filter_fields'))
        facet_names = set(plone_api.portal.get_registry_record(
            'ploneintranet.search.facet_fields'))
        options = [x for x in filter_names if x in facet_names]
        # content type is rendered separately by the UI
        if 'friendly_type_name' in options:
            options.remove('friendly_type_name')
        return options

    @memoize
    def get_keywords(self):
        ''' Return the keywords we are searching

        The keyword can be the one from SearchableText (direct search)
        or from SearchableText_filtered
        (in case of a search refinement through pat-subform)
        '''
        keywords = (
            self.request.form.get('SearchableText')
            or self.request.form.get('SearchableText_filtered')
        )
        # Sanitize keywords to be unicode
        if isinstance(keywords, str):
            keywords = keywords.decode('utf8')
        elif isinstance(keywords, list):
            keywords = [
                keyword.decode('utf8') for keyword in keywords if keyword
            ]
        return keywords

    def is_searching(self):
        ''' Check if the user is searching,
        i.e. we have something to query either on
        SearchableText_filtered or in SearchableText
        '''
        return bool(self.get_keywords())

    def is_filtering(self):
        ''' Check if the user is filtering,
        i.e. we have something in SearchableText_filtered
        '''
        return bool(self.request.get('SearchableText_filtered'))

    def get_filters(self):
        ''' Return the filters for this search
        '''
        form = self.request.form
        filters = {
            'tags': form.get('tags', []),
            'friendly_type_name': form.get('friendly_type_name', [])
        }

        if not self.is_filtering():
            return filters

        # If we are here it means that the filters were changed,
        # so we refine an existing search
        supported_filters = plone_api.portal.get_registry_record(
            'ploneintranet.search.filter_fields'
        )
        for key in supported_filters:
            value = form.get(key)
            if value:
                filters[key] = safe_unicode(value)
        return filters

    def get_sorting(self):
        ''' Get the requested sorting method

        Supported methods:
         - relevancy (default, returns None)
         - reverse creation date (returns '-created')
        '''
        # Get sorting method
        if self.request.get('results-sorting') == 'date':
            return '-created'

    @memoize
    def search_response(self):
        ''' Parse the parameters from the request
        and query the ISiteSearch utility
        '''
        if not self.is_searching():
            return []
        search_util = getUtility(ISiteSearch)
        response = search_util.query(
            self.get_keywords(),
            filters=self.get_filters(),
            start_date=self._extract_date('start_date'),
            end_date=self._extract_date('end_date'),
            start=self.get_start(),
            step=self._batch_size,
            sort=self.get_sorting(),
        )
        return response

    @forever.memoize
    def get_facet_type_class(self, value):
        """ Take the friendly type name (e.g. OpenOffice Write Document)
        and return a class for displaying the correct icon
        """
        value = value.lower()
        if 'word' in value:
            return 'type-word'
        if 'excel' in value:
            return 'type-excel'
        if 'pdf' in value:
            return 'type-pdf'
        if 'page' in value:
            return 'type-rich'
        if 'news' in value:
            return 'type-news'
        if 'event' in value:
            return 'type-event'
        if 'image' in value:
            return 'type-image'
        if 'presentation' in value:
            return 'type-powerpoint'
        if 'workspace' in value:
            return 'type-workspace'
        if 'link' in value:
            return 'type-link'
        if 'question' in value:
            return 'type-question'
        if 'audio' in value:
            return 'type-audio'
        if 'video' in value:
            return 'type-video'
        if 'contract' in value:
            return 'type-contract'
        if 'odt' in value:
            return 'type-odt'
        if 'openoffice' in value:
            return 'type-odt'
        if 'octet' in value:
            return 'type-octet'
        if 'postscript' in value:
            return 'type-postscript'
        if 'plain' in value:
            return 'type-plain-text'
        if 'archive' in value:
            return 'type-zip'
        if 'business card' in value:
            return 'type-business-card'
        if 'person' in value:
            return 'type-people'
        if 'ploneintranet.userprofile.userprofilecontainer':
            return 'super-space'
        # This is our fallback
        return self._facet_fallback_type_class

    @memoize
    def tag_facets(self):
        ''' Return the tags for faceting search results
        '''
        response = self.search_response()
        tags = response.facets.get('tags', [])
        tags = [
            {
                'id': getUtility(IIDNormalizer).normalize(t['name']),
                'title': t['name'],
                'counter': t['count'],
            }
            for t in tags
        ]
        tags.sort(key=lambda t: (-t['counter'], t['title'].lower()))
        return tags

    @memoize
    def type_facets(self):
        ''' Return the types for faceting search results
        '''
        response = self.search_response()
        types = response.facets.get('friendly_type_name', [])
        types = [
            {
                'id': self.get_facet_type_class(t['name']),
                'title': t['name'],
                'counter': t['count'],
            }
            for t in types
        ]
        types.sort(key=lambda t: (-t['counter'], t['title'].lower()))
        return types

    def show_previews(self):
        ''' Check if we have to display previews.

        According to the prototype this is controlled:
         - by the state of the checkbox 'display-previews'
           that appears in the options tooltip.
         - by a preference in the user profile

        BBB: For the time being the preview is always displayed
             when we search.
             When we filter it is controlled by
             a checkbox in the search options
        '''
        if self.is_filtering():
            # When we are accessing the form through the options tooltip,
            # we have the parameters submitted twice, resulting in a list
            if isinstance(self.request.get('options.submitted'), list):
                if self.request.get('display-previews-old'):
                    return self.request.get('display-previews') == ['on', 'on']
            return self.request.get('display-previews') == 'on'
        return True

    def search_by_type(self, type_name):
        """
        Search for specific content types
        """
        form = self.request.form
        keywords = form.get('SearchableText')
        if not keywords:
            return []
        filters = {'portal_type': type_name}

        search_util = getUtility(ISiteSearch)
        response = search_util.query(
            keywords,
            filters=filters,
        )
        return response

    def search_images(self):
        return self.search_by_type('Image')

    def search_files(self):
        return self.search_by_type('File')

    def search_people(self):
        return self.search_by_type('ploneintranet.userprofile.userprofile')
