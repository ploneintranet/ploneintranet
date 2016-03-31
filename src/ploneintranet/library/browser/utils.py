import logging

from plone import api
from plone.dexterity.utils import safe_unicode
from zope.component import getUtility

from ploneintranet.search.interfaces import ISiteSearch, ISearchResponse

log = logging.getLogger(__name__)


folderish = ['ploneintranet.library.section',
             'ploneintranet.library.folder']
pageish = ['Document', 'News Item', 'Link', 'File']
hidden = ['Image']
types_to_show = folderish + pageish


def sections_of(context):
    path_elements = context.getPhysicalPath()
    path = '/'.join(path_elements)
    path_depth = len(path_elements) + 1
    results = query(
        path=path, path_depth=path_depth, portal_types=types_to_show)
    struct = []
    for item in results:
        if item.portal_type in hidden:
            continue
        elif item.portal_type in folderish:
            type_ = 'container'
        elif item.portal_type in pageish:
            type_ = 'document'
        else:
            # to add: collection, newsitem, event, link, file
            type_ = 'unsupported'
            log.error("Unsupported type %s", item.portal_type)
        child = result2object(item)
        section = dict(title=item.title,
                       description=item.description,
                       absolute_url=item.url,
                       type=type_,
                       preview=item.preview_image_path,
                       context=child)
        section['content'] = children_of(child)
        struct.append(section)
    return struct


def children_of(context):
    if context.portal_type not in folderish:
        return []
    path_elements = context.getPhysicalPath()
    path = '/'.join(path_elements)
    path_depth = len(path_elements) + 1
    results = query(
        path=path, path_depth=path_depth, portal_types=types_to_show)
    content = []
    for item in results:
        if item.portal_type in hidden:
            continue
        elif item.portal_type in folderish:
            (follow, icon) = ("follow-section", "icon-squares")
        elif item.portal_type in pageish:
            (follow, icon) = ("follow-page", "icon-page")
        else:
            # to add: collection, newsitem, event, link, file
            log.error("Unsupported type %s", item.portal_type)
            (follow, icon) = ("follow-x", "icon-x")
        content.append(dict(
            title=item.title,
            absolute_url=item.url,
            follow=follow,
            icon=icon))
    return content


def query(path=None, path_depth=None, tags=[], portal_types=None,
          facet_by=None, sort_by=None,
          debug=False):
    """Helper method for Solr power search:
    - adds request_tag to search phrase
    - sorts on title
    """
    sitesearch = getUtility(ISiteSearch)
    Q = sitesearch.Q

    lucene_query = Q()
    if path:
        lucene_query &= Q(path_parents=path)
        if path_depth:
            lucene_query &= Q(path_depth=path_depth)
    for tag in tags:
        lucene_query &= Q(tags=safe_unicode(tag))
    if portal_types:
        subquery = Q()
        for pt in portal_types:
            subquery |= Q(portal_type=pt)
        lucene_query &= subquery

    solr_query = sitesearch._create_query_object(None)
    solr_query = solr_query.filter(lucene_query)
    if facet_by:
        solr_query = solr_query.facet_by(facet_by)
    if sort_by:
        solr_query = solr_query.sort_by(sort_by)
    if debug:
        solr_query = sitesearch._apply_debug(solr_query)

    response = sitesearch.execute(solr_query, debug=debug)
    return ISearchResponse(response)


def result2object(searchresult):
    """Return the object for this ISearchResult.

    This method mimicks a subset of what publisher's traversal does,
    so it allows access if the final object can be accessed even
    if intermediate objects cannot.

    Analogous to Products.ZCatalog.CatalogBrain.getObject()
    but without the fallbacks needed when there is no request
    i.e. in tests.
    """
    path = searchresult.path.split('/')
    root = api.portal.get()
    if len(path) > 1:
        parent = root.unrestrictedTraverse(path[:-1])
    else:
        parent = root
    # CatalogBrain has path[-1] without colon - breaks for me
    return parent.restrictedTraverse(path[-1:])
