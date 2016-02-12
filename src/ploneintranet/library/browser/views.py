import urllib

from logging import getLogger
from Products.Five import BrowserView
from plone import api
from plone.app.layout.globals.interfaces import IViewView
from plone.dexterity.utils import safe_unicode
from plone.memoize import view
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.library.browser import utils
from ploneintranet.search.interfaces import ISiteSearch, ISearchResponse

log = getLogger(__name__)


class LibraryHomeView(BrowserView):
    """
    The '/library' link in the portal tabs is coded as a CMF action
    and not derived from the actual library app URL.
    This view redirects to the, or a, actual LibraryApp/view.
    """
    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(portal_type='ploneintranet.library.app')
        if not results:
            msg = "Somebody removed the last library app and broke the site."
            log.error(msg)
            return msg
        target = results[0].getURL()

        if len(results) > 1:
            # pick the first one, unless there is one actually called 'libary'
            for brain in results:
                if brain.id == 'library':
                    target = brain.getURL()

        # get us to an actual LibraryAppView
        self.request.response.redirect(target)


class LibraryBaseView(BrowserView):

    groupby = 'section'
    groupby_menu_enabled = False
    enabled = True

    def selected(self, value):
        if value == self.groupby:
            return dict(selected=1)
        return {}

    def __call__(self):
        groupby = self.request.get('groupby', None)
        if not groupby:
            return super(LibraryBaseView, self).__call__()

        if groupby == 'section':
            self.request.response.redirect(self.context.absolute_url())
        elif groupby == 'tag':
            self.request.response.redirect('{}/tag'.format(
                self.context.absolute_url()))

    def app(self):
        return self.chain(getapp=True)

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
            raise AttributeError("Cannot find parent Library app!")

        if getapp:
            return obj
        return _chain

    @view.memoize
    def sections(self):
        """Return toplevel section navigation"""
        app = self.app()
        sections = app.objectValues()
        current_url = self.request['ACTUAL_URL']
        current_nav = app
        for s in sections:
            if current_url.startswith(s.absolute_url()):
                current_nav = s
                break

        app_current = (app == current_nav) and 'current' or ''
        menu = [dict(title=_("All topics"),
                     absolute_url=app.absolute_url(),
                     current=app_current)]

        for s in sections:
            s_current = (s == current_nav) and 'current' or ''
            menu.append(dict(title=s.Title,
                             absolute_url=s.absolute_url(),
                             current=s_current))
        return menu

    @view.memoize
    def children(self):
        """Return children and grandchildren of current context"""
        return utils.sections_of(self.context)

    def can_add(self):
        return api.user.has_permission('Add portal content',
                                       obj=self.context)

    def can_edit(self):
        return api.user.has_permission('Modify portal content',
                                       obj=self.context)


class LibraryAppView(LibraryBaseView):

    groupby_menu_enabled = True

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
        self.sitesearch = getUtility(ISiteSearch)
        self.request_tag = None
        self.enabled = True  # only in solr

    def publishTraverse(self, request, name):
        """Extract self.request_tag from URL /tag/foobar"""
        self.request_tag = safe_unicode(urllib.unquote(name))
        return self

    def query(self, path=None, tag=None, portal_types=None):
        """Helper method for Solr power search:
        - adds self.request_tag to search phrase
        - sorts on title
        """
        Q = self.sitesearch.Q
        _query = self.sitesearch.connection.query()
        lucene_query = Q()
        if path:
            lucene_query &= Q(path_parents=path)
        if tag:
            lucene_query &= Q(tags=safe_unicode(tag))
        if self.request_tag:
            lucene_query &= Q(tags=self.request_tag)
        if portal_types:
            subquery = Q()
            for pt in portal_types:
                subquery |= Q(portal_type=pt)
            lucene_query &= subquery

        _query = _query.filter(lucene_query)
        _query = _query.facet_by('tags')
        _query = _query.sort_by('Title')
        response = self.sitesearch.execute(_query)
        return ISearchResponse(response)

    def info(self):
        if self.request_tag:
            return dict(title=self.request_tag, klass='icon-tag')
        else:
            return {}

    def sections(self):
        """Toplevel section navigation, targets tag facet"""
        menu = super(LibraryTagView, self).sections()
        for section in menu:
            section['absolute_url'] += '/tag'
        return menu

    def children(self):
        """Catch error on non-supported ZCatalog"""
        try:
            return self._children()
        except UnicodeDecodeError:
            # happens on ZCatalog. Not supported here.
            self.enabled = False
            return []

    def _children(self):
        """Expose tag facet for library or section"""
        path = '/'.join(self.context.getPhysicalPath())
        response = self.query(path=path)
        struct = []
        for _tag in self._tags_facet(response):
            url = "%s/tag/%s" % (self.context.absolute_url(),
                                 urllib.quote(_tag.encode('utf8')))
            section = dict(title=_tag,
                           absolute_url=url,
                           type='tag',
                           subtags=[],
                           content=[])
            if self.request_tag:
                section['content'] = self._content_children(path, _tag)
            else:
                section['subtags'] = self._subtags_children(path, _tag)
            struct.append(section)
        return struct

    def _subtags_children(self, path, tag):
        """List tags co-occurring with <tag>"""
        response = self.query(path=path,
                              tag=tag)
        children = []
        for _tag in self._tags_facet(response):
            if _tag == tag:
                # work around poor zcatalog faceting implementation
                continue
            url = "%s/tag/%s" % (self.context.absolute_url(),
                                 urllib.quote(_tag.encode('utf8')))
            children.append(dict(title=_tag,
                                 absolute_url=url))
        return children

    def _content_children(self, path, tag):
        """List content tagged as <tag>"""
        response = self.query(path=path,
                              tag=tag,
                              portal_types=utils.pageish)
        children = []
        for child in response:
            children.append(dict(title=child.title,
                                 absolute_url=child.url))
        return children

    def _tags_facet(self, searchresponse):
        """
        ZCatalog returns <str> Solr returns <unicode>.
        We force everything into unicode and sort abc.
        """
        return sorted([safe_unicode(t)
                       for t in searchresponse.facets.get('tags', [])])
