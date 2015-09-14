import logging
from ploneintranet import api as pi_api
log = logging.getLogger(__name__)


folderish = ['ploneintranet.library.section',
             'ploneintranet.library.folder']
pageish = ['Document', 'News Item', 'Link', 'File']
hidden = ['Image']
types_to_show = folderish + pageish


def sections_of(context, **kwargs):
    if 'portal_type' not in kwargs:
        kwargs.update(portal_type=types_to_show)
    results = context.restrictedTraverse('@@folderListing')(**kwargs)
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
        if pi_api.previews.has_previews(child):
            preview = pi_api.previews.get_preview_urls(child)[0]
        else:
            preview = ''
        section = dict(title=item.title,
                       description=item.description,
                       absolute_url=item.getURL(),
                       type=type_,
                       preview=preview,
                       context=child)
        section['content'] = children_of(child)
        struct.append(section)
    return struct


def children_of(context, **kwargs):
    if context.portal_type not in folderish:
        return []
    if 'portal_type' not in kwargs:
        kwargs.update(portal_type=types_to_show)
    results = context.restrictedTraverse('@@folderListing')(**kwargs)
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
            absolute_url=item.getURL(),
            follow=follow,
            icon=icon))
    return content
