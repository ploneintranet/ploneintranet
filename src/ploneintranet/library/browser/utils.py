import logging

log = logging.getLogger(__name__)


folderish = ('ploneintranet.library.section',
             'ploneintranet.library.folder')
pageish = ('Document', 'News Item', 'Link', 'File')
hidden = ('Image')


def sections_of(context):
    struct = []
    for child in context.objectValues():
        if child.portal_type in hidden:
            continue
        elif child.portal_type in folderish:
            type_ = 'container'
        elif child.portal_type in pageish:
            type_ = 'document'
        else:
            # to add: collection, newsitem, event, link, file
            type_ = 'unsupported'
            log.error("Unsupported type %s", child.portal_type)
        section = dict(title=child.Title(),
                       description=child.Description(),
                       absolute_url=child.absolute_url(),
                       type=type_,
                       context=child)
        section['content'] = children_of(child)
        struct.append(section)
    return struct


def children_of(context):
    content = []
    for child in context.objectValues():
        if child.portal_type in hidden:
            continue
        elif child.portal_type in folderish:
            (follow, icon) = ("follow-section", "icon-squares")
        elif child.portal_type in pageish:
            (follow, icon) = ("follow-page", "icon-page")
        else:
            # to add: collection, newsitem, event, link, file
            log.error("Unsupported type %s", child.portal_type)
            (follow, icon) = ("follow-x", "icon-x")
        content.append(dict(
            title=child.Title(),
            absolute_url=child.absolute_url(),
            follow=follow,
            icon=icon))
    return content
