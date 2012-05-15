from zope.interface import Interface
from zope.interface import Attribute


class IActivity(Interface):

    getURL = Attribute("url")
    Title = Attribute("title")
    portal_type = Attribute("portal_type")
    render_type = Attribute("render_type")
    is_status = Attribute("is_status")
    is_discussion = Attribute("is_discussion")
    is_content = Attribute("is_content")
    userid = Attribute("userid")
    Creator = Attribute("creator")
    has_author_link = Attribute("author home url is not None")
    author_home_url = Attribute("author home url")
    portrait_url = Attribute("author portrait url")
    date = Attribute("formatted datetime")
    getText = Attribute("text")
