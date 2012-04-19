from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_chain

from plone.app.discussion.browser.comments import CommentForm, CommentsViewlet


class Form(CommentForm):

    pass


class Comments(CommentsViewlet):
    """Subclass the p.a.discussion comments viewlet
    and change it's behaviour to suit our purposes."""

    form = Form
    index = ViewPageTemplateFile('comments.pt')

    comment_transform_message = "What's on your mind?"

    def __init__(self, *args, **kwargs):
        CommentsViewlet.__init__(self, *args, **kwargs)
        # force microblog context to SiteRoot singleton
        for obj in aq_chain(self.context):
            if IPloneSiteRoot.providedBy(obj):
                self.context = obj
                return
