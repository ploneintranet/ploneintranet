from zope.interface import Interface
from zope.interface import implementer
from zope.component import getMultiAdapter
from plone import api
from plone.tiles import Tile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder


class INavigationTile(Interface):
    """Marker interface for the navigation tile
    """


class WorkspaceQueryBuilder(SitemapQueryBuilder):

    def __init__(self, context, root):
        super(WorkspaceQueryBuilder, self).__init__(context)
        if 'path' in self.query:
            self.query['path']['query'] = '/'.join(root.getPhysicalPath())
            if 'navtree' in self.query:
                del self.query['navtree']
            if 'navtree_start' in self.query:
                del self.query['navtree_start']
            self.query['path']['depth'] = 1


@implementer(INavigationTile)
class NavigationTile(Tile):

    index = ViewPageTemplateFile('templates/navigation.pt')

    def items(self):
        # TODO: use transient tiles with schema and data manager here
        root = self.request.form.get('root')
        if root:
            root = api.content.get(UID=root)
        else:
            root = self.context
        query_builder = WorkspaceQueryBuilder(self.context, root)
        strategy = getMultiAdapter((self.context, None), INavtreeStrategy)
        strategy.showAllParents = False
        strategy.rootPath = '/'.join(root.getPhysicalPath())

        tree = buildFolderTree(
            self.context,
            obj=self.context,
            query=query_builder(),
            strategy=strategy
        )
        return tree['children']

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
