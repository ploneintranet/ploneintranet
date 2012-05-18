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

    portal_type = Attribute("portal_type")
    render_type = Attribute("render_type")
    is_status = Attribute("is_status")
    is_discussion = Attribute("is_discussion")
    is_content = Attribute("is_content")
