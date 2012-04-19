from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.discussion.browser.comments import CommentForm, CommentsViewlet


class Form(CommentForm):

    pass


class Comments(CommentsViewlet):
    """Subclass the p.a.discussion comments viewlet
    and change it's behaviour to suit our purposes."""

    form = Form
    index = ViewPageTemplateFile('comments.pt')

    comment_transform_message = "What's on your mind?"
