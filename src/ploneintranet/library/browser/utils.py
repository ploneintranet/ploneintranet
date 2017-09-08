# coding=utf-8
from plone.dexterity.utils import safe_unicode
from ploneintranet.search.interfaces import ISearchResponse
from ploneintranet.search.interfaces import ISiteSearch
from zope.component import getUtility

import logging


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
        path=path, path_depth=path_depth, portal_types=types_to_show,
        sort_by='getObjPositionInParent')
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
        child = item.getObject()
        section = dict(title=item.title,
                       id=item.getId(),
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
        path=path, path_depth=path_depth, portal_types=types_to_show,
        sort_by='getObjPositionInParent')
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
            id=item.getId(),
            absolute_url=item.url,
            follow=follow,
            icon=icon))
    return content


def query(
    path=None,
    path_depth=None,
    tags=[],
    portal_types=None,
    facet_by=None,
    sort_by=None,
    searchable_text=None,
    debug=False,
):
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
        if not isinstance(path_depth, (list, tuple)):
            lucene_query &= Q(path_depth=path_depth)
        else:
            subquery = Q()
            for pd in path_depth:
                subquery |= Q(path_depth=pd)
            lucene_query &= subquery
    tags = tags or []
    if isinstance(tags, basestring):
        tags = [tags]
    for tag in tags:
        lucene_query &= Q(tags=safe_unicode(tag))
    if portal_types:
        subquery = Q()
        for pt in portal_types:
            subquery |= Q(portal_type=pt)
        lucene_query &= subquery
    if searchable_text:
        lucene_query &= Q(SearchableText=safe_unicode(searchable_text))
    solr_query = sitesearch._create_query_object(None)
    solr_query = solr_query.filter(lucene_query)
    if facet_by:
        solr_query = solr_query.facet_by(facet_by)
    if sort_by:
        if isinstance(sort_by, basestring):
            sort_by = [sort_by]
        for sb in sort_by:
            solr_query = solr_query.sort_by(sb)
    if debug:
        solr_query = sitesearch._apply_debug(solr_query)

    response = sitesearch.execute(
        solr_query.paginate(rows=99999),
        debug=debug
    )
    return ISearchResponse(response)
