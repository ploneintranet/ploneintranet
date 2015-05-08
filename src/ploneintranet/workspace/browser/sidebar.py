# from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.tiles import Tile
from ploneintranet.workspace.utils import TYPE_MAP
from zope.publisher.browser import BrowserView

FOLDERISH_TYPES = ['folder']


class Sidebar(BrowserView):

    """ A view to serve as a sidebar navigation for workspaces
    """


class ContentItemsTile(Tile):

    index = ViewPageTemplateFile("templates/sidebar-contentitems.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def parent(self):
        if self.context.portal_type == (
                "ploneintranet.workspace.workspacefolder"):
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
                    "source: #sidebar-content; target: #sidebar-content"
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
