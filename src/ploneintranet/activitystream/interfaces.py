from zope.interface import Interface


class IStatusActivityReply(Interface):
    """ Deprecated. Do not use.

    Only here for BBB purposes to avoid crashing alsoProvides index
    on older statusupdates that may provide this marker interface.
    """
