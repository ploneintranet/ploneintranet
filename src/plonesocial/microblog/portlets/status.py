from z3c.form import form, button

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_chain

from plone.app.discussion.browser.comments import CommentForm, CommentsViewlet
from plone.app.discussion import PloneAppDiscussionMessageFactory as _


class StatusForm(CommentForm):
    """
    re-add the button and handler on a different name
    so we don't get double form processing
    and double comment creation
    """
    form.extends(CommentForm, ignoreButtons=True, ignoreHandlers=True)

    def updateActions(self):
        super(CommentForm, self).updateActions()
        self.actions['cancel'].addClass("standalone")
        self.actions['cancel'].addClass("hide")
        self.actions['status'].addClass("context")

    @button.buttonAndHandler(_(u"add_comment_button", default=u"Comment"),
                             name='status')
    def handleStatus(self, action):
        # unwrap CommentForm.handleComment from it's decorator
        # depends on z3c.form.button.Handler implementation detail
        CommentForm.handleComment.func(self, action)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        # This method should never be called, it's only there to show
        # a cancel button that is handled by a jQuery method.
        pass  # pragma: no cover


class StatusViewlet(CommentsViewlet):
    """Subclass the p.a.discussion comments viewlet
    and change it's behaviour to suit our purposes."""

    form = StatusForm
    index = ViewPageTemplateFile('status.pt')

    comment_transform_message = "What's on your mind?"

    def __init__(self, compact, *args, **kwargs):
        CommentsViewlet.__init__(self, *args, **kwargs)
        self.compact = compact
        # force microblog context to SiteRoot singleton
        for obj in aq_chain(self.context):
            if IPloneSiteRoot.providedBy(obj):
                self.context = obj
                return
