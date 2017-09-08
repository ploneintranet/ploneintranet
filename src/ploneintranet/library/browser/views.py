# coding=utf-8
from collections import OrderedDict
from logging import getLogger
from plone import api
from plone.app.layout.globals.interfaces import IViewView
from plone.dexterity.utils import safe_unicode
from plone.memoize import view
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.library.browser import utils
from Products.Five import BrowserView
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

import urllib


log = getLogger(__name__)


class LibraryHomeView(BrowserView):
    '''
    The '/library' link in the portal tabs is coded as a CMF action
    and not derived from the actual library app URL.
    This view redirects to the, or a, actual LibraryApp/view.
    '''
    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(portal_type='ploneintranet.library.app')
        if not results:
            msg = 'Somebody removed the last library app and broke the site.'
            log.error(msg)
            return msg
        target = results[0].getURL()

        if len(results) > 1:
            # pick the first one, unless there is one actually called 'libary'
            for brain in results:
                if brain.id == 'library':
                    target = '{url}?{qs}'.format(
                        brain.getURL(),
                        urllib.urlencode(self.request.form)
                    )

        # get us to an actual LibraryAppView
        self.request.response.redirect(target)


class LibraryBaseView(BrowserView):

    groupby = 'section'
    groupby_menu_enabled = False
    enabled = True
    folderish_portal_types = (
        'ploneintranet.library.section',
        'ploneintranet.library.folder'
    )
    pageish_portal_types = (
        'Document',
        'File',
        'Link',
        'News Item',
    )
    show_searchbox = False

    def __call__(self):
        groupby = self.request.form.pop('groupby', None)
        if groupby != 'tag':
            return super(LibraryBaseView, self).__call__()

        target = self.context.absolute_url() + '/tag'
        if self.request.form:
            target += ('?' + urllib.urlencode(self.request.form))
        self.request.response.redirect(target)

    @view.memoize
    def chain(self, getapp=False):
        _chain = []
        obj = self.context
        while (obj.portal_type != 'ploneintranet.library.app' and
               obj.portal_type != 'Plone Site'):
            _chain.insert(0, dict(title=obj.Title,
                                  absolute_url=obj.absolute_url()))
            obj = obj.aq_inner.aq_parent

        if obj.portal_type == 'Plone Site':
            raise AttributeError('Cannot find parent Library app!')

        if getapp:
            return obj
        return _chain

    @view.memoize
    def app(self):
        return self.chain(getapp=True)

    def can_add(self):
        return api.user.has_permission('Add portal content',
                                       obj=self.context)

    def can_edit(self):
        return api.user.has_permission('Modify portal content',
                                       obj=self.context)

    @view.memoize
    def sections(self):
        '''Return toplevel section navigation'''
        app = self.app()
        # The first navigation entry is always the app.
        # It is highlighted with the 'current class'
        # if the context is equal to that app
        menu = [dict(title=_('All topics'),
                     absolute_url=app.absolute_url(),
                     current='current' if self.context == app else None)]
        # Then we look for the contained sections
        # and create the other navigation items
        sections = utils.query(
            '/'.join(app.getPhysicalPath()),
            portal_types=['ploneintranet.library.section'],
        )
        context_url = self.context.absolute_url()
        menu.extend([
            dict(
                title=section.title,
                absolute_url=section.url,
                current='current' if section.url in context_url else None,
            ) for section in sections
        ])
        return menu

    def get_child_class(self, child):
        ''' Get the class for the chiod elements
        '''
        if child.portal_type in self.pageish_portal_types:
            return 'type-page'
        return 'group-by-{}'.format(self.groupby)

    @property
    def solr_params(self):
        ''' Return the parameters for the solr query
        '''
        searchable_text = self.request.get('SearchableText', '').lower()
        path = '/'.join(self.context.getPhysicalPath())
        params = {
            'path': path,
            'searchable_text': searchable_text,
            'sort_by': 'getObjPositionInParent',
        }
        if searchable_text:
            # We want all the pageish types under this context
            params['portal_types'] = self.pageish_portal_types
        else:
            # Otherwise we want all the children and nephews of this page
            params['path_depth'] = [
                path.count('/') + 2,
                path.count('/') + 3,
            ]
            params['portal_types'] = (
                self.folderish_portal_types + self.pageish_portal_types
            )
        return params

    @view.memoize
    def get_logical_parent(self, parent_path):
        ''' Memoized version of restrictedTraverse

        We expect the path to be the absoilute path,
        so we need to strip out this context's path
        '''
        context_path = '/'.join(self.context.getPhysicalPath())
        if isinstance(parent_path, unicode):
            parent_path = parent_path.encode('utf8')
        if context_path == parent_path:
            # We want to return None in this case because
            # the children does not need to be group
            return
        # Get the relative path
        parent_path = parent_path[len(context_path) + 1:]
        return self.context.restrictedTraverse(parent_path, None)

    def structure_solr_results(self, results):
        ''' Take the solr results and create a nested structure
        to fill the page template tiles
        '''
        children = OrderedDict()
        for result in results:
            parent_path = result.path.rpartition('/')[0]
            parent = self.get_logical_parent(parent_path)
            # If there is no logical parent
            # consider the result as a child of this folder
            child = parent or result.getObject()
            if child not in children:
                children[child] = []
            if parent:
                children[child].append(result)
        return children

    @view.memoize
    def children(self):
        '''Return children and nephews of current context'''
        results = utils.query(**self.solr_params)
        return self.structure_solr_results(results)


class LibraryAppView(LibraryBaseView):

    groupby_menu_enabled = True
    show_searchbox = True

    def info(self):
        return {}


class LibrarySectionView(LibraryBaseView):

    groupby_menu_enabled = True

    def info(self):
        return dict(title=self.context.Title,
                    description=self.context.Description)


class LibraryFolderView(LibraryBaseView):

    def info(self):
        return dict(
            chain=self.chain(),
            description=self.context.Description)


class LibraryTagView(LibraryBaseView):

    implements(IPublishTraverse, IViewView)

    groupby = 'tag'
    groupby_menu_enabled = True

    def __init__(self, context, request):
        super(LibraryTagView, self).__init__(context, request)
        self.request_tag = None
        self.enabled = True  # only in solr

    def publishTraverse(self, request, name):
        '''Extract self.request_tag from URL /tag/foobar'''
        self.request_tag = safe_unicode(urllib.unquote(name))
        return self

    def info(self):
        if self.request_tag:
            return dict(title=self.request_tag, klass='icon-tag')
        else:
            return {}

    def sections(self):
        '''Toplevel section navigation, targets tag facet'''
        menu = super(LibraryTagView, self).sections()
        for section in menu:
            section['absolute_url'] += '/tag'
        return menu

    @property
    def solr_params(self):
        ''' Return the parameters for the solr query
        '''
        searchable_text = self.request.get('SearchableText', '').lower()
        params = {
            'facet_by': 'tags',
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_types': self.pageish_portal_types,
            'searchable_text': searchable_text,
            'tags': self.request_tag,
            'sort_by': 'Title',
        }
        return params

    @property
    @view.memoize
    def tag_factory(self):
        class Tag(object):
            portal_type = None
            url_template = '/'.join((
                self.context.absolute_url(),
                'tag',
                '{}',
            ))

            def __init__(self, tag):
                self.title = tag
                self.url = self.url_template.format(
                    urllib.quote(tag.encode('utf8'))
                )

        return Tag

    def maybe_taggify(self, obj):
        ''' If obj is a string (a tag) we call the tag_factory
        to have an object that can be easily rendered by our template
        '''
        if not isinstance(obj, basestring):
            return obj
        return self.tag_factory(obj)

    def structure_solr_results(self, results):
        ''' Take the solr results and create a nested structure
        to fill the page template tiles
        '''
        # We take all the tags in the query
        # different from the currently requested one
        tags = [
            tag['name'] for tag in results.facets.get('tags', [])
            if tag['name'] != self.request_tag
        ]
        # We initialize our structure
        # It is temporary because we want to sort it later
        tmp_children = {tag: set() for tag in tags}
        # Finally we can fill our structure
        # For each result we want to update the structure
        # with the additional tags and maybe the document
        # if we are already filtering
        # If filtering is in place we just show the nested tags
        include_results = (
            self.request_tag or self.request.get('SearchableText')
        )
        tags_set = set(tags)
        for result in results:
            result_tags = tags_set.intersection(result.Subject())
            if not result_tags:
                # No relevant tags for this document, it will be a child
                tmp_children[result] = set()
            else:
                for result_tag in result_tags:
                    tmp_children[result_tag].update(result_tags)
                    if include_results:
                        tmp_children[result_tag].add(result)
        # Now we sort the data structure
        # First all the tags and then all the documents
        children = OrderedDict()
        tmp_child_keys = sorted(
            tmp_children,
            key=lambda x: (
                hasattr(x, 'portal_type'),
                x.title.lower() if hasattr(x, 'portal_type') else x.lower()
            )
        )
        for tmp_child in tmp_child_keys:
            tmp_values = tmp_children[tmp_child]
            child = self.maybe_taggify(tmp_child)
            if child not in children:
                children[child] = []
            for tmp_value in tmp_values:
                # Skip tags that happen to be nested
                if tmp_value != tmp_child:
                    children[child].append(self.maybe_taggify(tmp_value))
            # Sort the children, first by pportal_type and the by title
            children[child].sort(key=lambda x: (x.portal_type, x.title))
        return children

    def __call__(self):
        groupby = self.request.form.pop('groupby', None)
        if groupby != 'section':
            return super(LibraryBaseView, self).__call__()

        target = self.context.absolute_url()
        if self.request.form:
            target += ('?' + urllib.urlencode(self.request.form))
        self.request.response.redirect(target)
