from zope.interface import Interface, Attribute


class IPloneintranetLayoutLayer(Interface):
    """Marker interface for ploneintranet.layout installed"""


class IAppLayer(Interface):
    """
    Mixin for browser layer to mark a Zope 3 browser layer as only
    being applicable within a specific IAppContainer
    """


class IAppContainer(Interface):
    """
    Mixin for content interface to mark a content object in which
    a specific IAppLayer should be activated on traversal.
    """

    layer = Attribute("The IAppLayer to be activated on traversal")


class IAppManager(Interface):
    """
    Content interface to mark a content object as listable
    in the "Apps" section.
    """
    # extra attributes check Cornelis
    title = Attribute("Title of the app")
    icon = Attribute("Icon")


class IAppTile(Interface):
    """
    Tile interface to indicate a tile as listable on
    the dashboard.
    """
    # Nothing implemented yet
    # - coordinate with Cornelis
    # - bring existing tiles in line


# -- test fixture installed by profiles/testing --


class IMockLayer(IAppLayer):
    pass
