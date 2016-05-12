from zope.interface import Interface


class IPloneintranetUserprofileLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class IMembershipResolver(Interface):
    """
        Marker interface for non-SiteRoot objects which define local
        membership. Such objects must provide a `members` property.
    """

    def members():
        """ Returns a list of member ids """
