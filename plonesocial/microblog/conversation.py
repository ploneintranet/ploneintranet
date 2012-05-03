from zope.interface import implements, implementer
from zope.component import adapts, adapter
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from Acquisition import aq_base

try:
    from plone.app.async.interfaces import IAsyncService
    have_async = True
except ImportError:
    have_async = False

from Products.CMFPlone.Portal import PloneSite
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion import conversation as pad_conversation


def addStatus(context, comment):
    # resolve siteroot context to conversation
    conversation = IConversation(context)
    # we're already in the async worker, don't loop
    conversation.addComment(comment, do_async=False)


class StatusConversation(pad_conversation.Conversation):

    implements(IConversation)

    def addComment(self, comment, do_async=have_async):
        """Wrap the p.a.d.conversation.Conversation.addComment
        in a way that allows async dispatch.
        """
        import pdb; pdb.set_trace()
        if do_async:
            async = getUtility(IAsyncService)
            # use SiteRoot as async context
            async.queueJob(addStatus, self.__parent__, comment)
            # deferred insertion, we can't return the actual id
            return ''
        else:
            return pad_conversation.Conversation.addComment(self, comment)


@implementer(IConversation)
@adapter(PloneSite)
def statusConversationAdapterFactory(content):
    """
    Adapter factory to fetch the default conversation from annotations.

    Intercept p.a.d.browser.comments IConversation(__parent__)
    adapter lookup:

    An adapter registered for a class (PloneSite) is more specific
    than an adapter registered for an interface (IAnnotatable)
    """
    annotions = IAnnotations(content)
    if not pad_conversation.ANNOTATION_KEY in annotions:
        conversation = StatusConversation()
        conversation.__parent__ = aq_base(content)
    else:
        conversation = annotions[pad_conversation.ANNOTATION_KEY]
    return conversation.__of__(content)


class StatusConversationReplies(pad_conversation.ConversationReplies):
    """An IReplies adapter for status conversations.

    This makes it easy to work with top-level comments.

    An adapter registered for an interface implemented by a
    given class is more specific than an adapter registered
    for an interface implemented by a base class
    """
    implements(IReplies)
    # upstream adapts class not interface
    adapts(StatusConversation)


# no need to also subclass CommentReplies - use upstream is ok
