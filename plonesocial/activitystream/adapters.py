from zope.interface import implements
from zope.component import adapts
from DateTime import DateTime

from Products.ZCatalog.interfaces import ICatalogBrain
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName

from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.activitystream.interfaces import IActivity


class AbstractActivity(object):

    def get_user_home_url(self, username=None):
        if username is None:
            return None
        else:
            return "%s/author/%s" % (self.context.portal_url(), username)

    def get_user_portrait(self, username=None):
        if username is None:
            # return the default user image if no username is given
            return 'defaultUser.gif'
        else:
            portal_membership = getToolByName(self.context,
                                              'portal_membership',
                                              None)
            return portal_membership.getPersonalPortrait(username)\
                   .absolute_url()

    def format_time(self, time):
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        if hasattr(time, 'isoformat'):
            zope_time = DateTime(time.isoformat())
        else:
            # already a Zope DateTime
            zope_time = time
        util = getToolByName(self.context, 'translation_service')
        if DateTime().Date() == zope_time.Date():
            return util.toLocalizedTime(zope_time,
                                        long_format=True,
                                        time_only=True)
        else:
            # time_only=False still returns time only
            return util.toLocalizedTime(zope_time,
                                        long_format=True)

    @property
    def has_author_link(self):
        return self.get_user_home_url(self.userid) is not None

    @property
    def author_home_url(self):
        return self.get_user_home_url(self.userid)

    @property
    def portrait_url(self):
        return self.get_user_portrait(self.userid)

    @property
    def date(self):
        return self.format_time(self.raw_date)

    ## non-interface template compatibility

    @property
    def getURL(self):
        return self.url

    @property
    def getText(self):
        return self.text

    @property
    def Title(self):
        return self.title


class StatusActivity(AbstractActivity):
    implements(IActivity)
    adapts(IStatusUpdate)

    is_status = True
    is_discussion = is_content = False

    def __init__(self, context):
        self.context = context
        self.text = context.text
        self.title = ''
        self.url = ''
        self.portal_type = 'StatusUpdate'
        self.render_type = 'status'
        self.Creator = context.creator
        self.userid = context.userid
        self.raw_date = context.date


class BrainActivity(AbstractActivity):
    implements(IActivity)
    adapts(ICatalogBrain)

    is_status = False

    def __init__(self, context):
        self.context = context
        obj = context.getObject()
        self.title = obj.Title()
        self.url = context.getURL()
        self.portal_type = obj.portal_type
        self.Creator = obj.Creator()
        self.raw_date = obj.creation_date

        if obj.portal_type == 'Discussion Item':
            self.render_type = 'discussion'
            self.userid = obj.author_username
            self.text = obj.getText()
            # obj: DiscussionItem
            # parent: Conversation
            # grandparent: content object
            _contentparent = aq_parent(aq_parent(aq_inner(obj)))
            self.title = _contentparent.Title()
        else:
            self.userid = obj.getOwnerTuple()[1]
            self.render_type = 'content'
            self.text = obj.Description()

    @property
    def is_discussion(self):
        return self.render_type == 'discussion'

    @property
    def is_content(self):
        return self.render_type == 'content'
