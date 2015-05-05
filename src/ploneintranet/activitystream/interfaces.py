from zope.interface import Interface
from zope.interface import Attribute


class IActivity(Interface):
    """Core content-ish accessors"""
    getURL = Attribute("url")
    Title = Attribute("title")
    userid = Attribute("userid")
    Creator = Attribute("creator")
    getText = Attribute("text")
    raw_date = Attribute("raw date")
    getId = Attribute("activity id")

    portal_type = Attribute("portal_type")
    render_type = Attribute("render_type")


class IStatusActivity(IActivity):
    """IActivity for an IStatusUpdate"""

    def replies():
        """ Return a list of replies (IStatusActivity) to this activity"""


class IStatusActivityReply(IStatusActivity):
    """ A reply to a IStatusActivity """
