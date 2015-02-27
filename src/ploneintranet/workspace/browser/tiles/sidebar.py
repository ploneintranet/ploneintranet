# from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.tiles import Tile
from ploneintranet.workspace.utils import TYPE_MAP
from ploneintranet.workspace.utils import parent_workspace
from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from plone import api
from collective.workspace.interfaces import IWorkspace
from plone.memoize.instance import memoize
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import _checkPermission as checkPermission

FOLDERISH_TYPES = ['folder']


class Sidebar(BrowserView):

    """ A view to serve as a sidebar navigation for workspaces
    """

    index = ViewPageTemplateFile("templates/sidebar.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def users(self):
        """Get current users and add in any search results.

        :returns: a list of dicts with keys
         - id
         - title
        :rtype: list
        """
        existing_users = self.existing_users()
        existing_user_ids = [x['id'] for x in existing_users]

        # Only add search results that are not already members
        sharing = getMultiAdapter((self.context, self.request),
                                  name='sharing')
        search_results = sharing.user_search_results()
        users = existing_users + [x for x in search_results
                                  if x['id'] not in existing_user_ids]

        users.sort(key=lambda x: safe_unicode(x["title"]))
        return users

    def my_workspace(self):
        return parent_workspace(self)

    @memoize
    def existing_users(self):

        members = IWorkspace(self.context).members
        info = []
        for userid, details in members.items():
            user = api.user.get(userid).getUser()
            title = user.getProperty('fullname') or user.getId() or userid
            info.append(
                dict(
                    id=userid,
                    title=title,
                    member=True,
                    admin='Admins' in details['groups'],
                )
            )

        return info

    def can_manage_workspace(self):
        """
        does this user have permission to manage the workspace
        """
        return checkPermission(
            "ploneintranet.workspace: Manage workspace",
            self.context,
        )

    # ContentItems

    def parent(self):
        if self.context.portal_type == \
                "ploneintranet.workspace.workspacefolder":
            return None
        parent = self.context.aq_parent
        return {'id': parent.getId(),
                'title': parent.Title(),
                'url': parent.absolute_url() + '/@@sidebar.default'}

    def children(self):
        """ returns a list of dicts of items in the current context
        """
        items = []
        catalog = self.context.portal_catalog
        current_path = '/'.join(self.context.getPhysicalPath())

        sidebar_search = self.request.get('sidebar-search', None)
        if sidebar_search:
            st = '%s*' % sidebar_search  # XXX plone only allows * as postfix.
            # With solr we might want to do real substr
            results = catalog.searchResults(SearchableText=st,
                                            path=current_path)
        else:
            results = self.context.getFolderContents()

        for item in results:
            # Do some checks to set the right classes for icons and candy
            desc = (
                item['Description']
                and 'has-description'
                or 'has-no-description'
            )

            content_type = TYPE_MAP.get(item['portal_type'], 'none')

            mime_type = ''  # XXX: will be needed later for grouping by mimetyp
            # typ can be user, folder, date and mime typish
            typ = 'folder'  # XXX: This needs to get dynamic later

            if content_type in FOLDERISH_TYPES:
                dpi = (
                    "source: #items; target: #items && "
                    "source: #selector-contextual-functions; "
                    "target: #selector-contextual-functions && "
                    "source: #context-title; target: #context-title && "
                    "source: #sidebar-search-form; "
                    "target: #sidebar-search-form"
                )
                url = item.getURL() + '/@@sidebar.default#items'
                content_type = 'group'
            else:
                dpi = "target: #document-body"
                url = item.getURL() + "#document-body"
                content_type = 'document'

            cls = 'item %s type-%s %s' % (content_type, typ, desc)

            items.append({
                'id': item['getId'],
                'cls': cls,
                'title': item['Title'],
                'description': item['Description'],
                'url': url,
                'type': TYPE_MAP.get(item['portal_type'], 'none'),
                'mime-type': mime_type,
                'dpi': dpi})
        return items

    ### Events

    # Nothing yet

    ### Tasks

    # Nothing yet







    


# class EventsTile(BrowserView):

#     """ A view for workspace events
#     """

#     index = ViewPageTemplateFile("templates/sidebar-events.pt")

#     def render(self):
#         return self.index()

#     def __call__(self):
#         return self.render()

# class TasksTile(BrowserView):

#     """ A view for workspace tasks
#     """

#     index = ViewPageTemplateFile("templates/sidebar-tasks.pt")

#     def render(self):
#         return self.index()

#     def __call__(self):
#         return self.render()


# class InfoTile(Tile):



# class ContentItemsTile(Tile):

#     index = ViewPageTemplateFile("templates/sidebar-contentitems.pt")

#     def render(self):
#         return self.index()

#     def __call__(self):
#         return self.render()

#     def parent(self):
#         if self.context.portal_type == \
#                 "ploneintranet.workspace.workspacefolder":
#             return None
#         parent = self.context.aq_parent
#         return {'id': parent.getId(),
#                 'title': parent.Title(),
#                 'url': parent.absolute_url() + '/@@sidebar.default'}

#     def children(self):
#         """ returns a list of dicts of items in the current context
#         """
#         items = []
#         catalog = self.context.portal_catalog
#         current_path = '/'.join(self.context.getPhysicalPath())

#         sidebar_search = self.request.get('sidebar-search', None)
#         if sidebar_search:
#             st = '%s*' % sidebar_search  # XXX plone only allows * as postfix.
#             # With solr we might want to do real substr
#             results = catalog.searchResults(SearchableText=st,
#                                             path=current_path)
#         else:
#             results = self.context.getFolderContents()

#         for item in results:
#             # Do some checks to set the right classes for icons and candy
#             desc = (
#                 item['Description']
#                 and 'has-description'
#                 or 'has-no-description'
#             )

#             content_type = TYPE_MAP.get(item['portal_type'], 'none')

#             mime_type = ''  # XXX: will be needed later for grouping by mimetyp
#             # typ can be user, folder, date and mime typish
#             typ = 'folder'  # XXX: This needs to get dynamic later

#             if content_type in FOLDERISH_TYPES:
#                 dpi = (
#                     "source: #items; target: #items && "
#                     "source: #selector-contextual-functions; "
#                     "target: #selector-contextual-functions && "
#                     "source: #context-title; target: #context-title && "
#                     "source: #sidebar-search-form; "
#                     "target: #sidebar-search-form"
#                 )
#                 url = item.getURL() + '/@@sidebar.default#items'
#                 content_type = 'group'
#             else:
#                 dpi = "target: #document-body"
#                 url = item.getURL() + "#document-body"
#                 content_type = 'document'

#             cls = 'item %s type-%s %s' % (content_type, typ, desc)

#             items.append({
#                 'id': item['getId'],
#                 'cls': cls,
#                 'title': item['Title'],
#                 'description': item['Description'],
#                 'url': url,
#                 'type': TYPE_MAP.get(item['portal_type'], 'none'),
#                 'mime-type': mime_type,
#                 'dpi': dpi})
#         return items
