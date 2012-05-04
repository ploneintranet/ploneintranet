from zope.interface import implements, implementer
from zope.component import adapts, adapter
from zope.component import getUtility
from zope.annotation.interfaces import IAnnotations
from Acquisition import aq_base
from Products.CMFPlone.Portal import PloneSite
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion import conversation as pad_conversation
import transaction

from persistent import Persistent

try:
    from plone.app.async.interfaces import IAsyncService
    have_async = True
except ImportError:
    have_async = False


ANNOTATION_KEY = pad_conversation.ANNOTATION_KEY

class Debug(Persistent):
    pass


def addStatus(context, comment):

#    annotations = IAnnotations(context)
#    annotations['debug'] = Debug()
#    annotations['debug'].someattr = 'somevalue'
#    return

    # resolve siteroot context to conversation
    conversation = IConversation(context)  # StatusConversation
    # we're already in the async worker, don't loop
    conversation.addComment(comment, do_async=False)


def dummy(context):
    pass


class StatusConversation(pad_conversation.Conversation):

    implements(IConversation)

    def addComment(self, comment, do_async=have_async):
        """Wrap the p.a.d.conversation.Conversation.addComment
        in a way that allows async dispatch.
        """
        if do_async:
#            addStatus(self.__parent__, comment)
#            return

            async = getUtility(IAsyncService)
            # use PloneSite context to avoid ++conversation++ traversal error
            async.queueJob(addStatus, self.__parent__, comment)
            # deferred insertion, we can't return the actual id
            # that will be used as a url fragment by p.a.d.
            return '?async=1'
        else:
#            import pdb; pdb.set_trace()
            id = pad_conversation.Conversation.addComment(self, comment)
#            transaction.commit()
            return id


@implementer(IConversation)
@adapter(PloneSite)  # override p.a.d. IAnnotatable adapter
def statusConversationAdapterFactory(content):
    """
    Adapter factory to fetch the default conversation from annotations.

    Intercept p.a.d.browser.comments IConversation(__parent__)
    adapter lookup:

    An adapter registered for a class (PloneSite) is more specific
    than an adapter registered for an interface (IAnnotatable)
    """
    annotions = IAnnotations(content)
    if not ANNOTATION_KEY in annotions:
        # first-time setup
        conversation = StatusConversation()
        conversation.__parent__ = aq_base(content)

        # pre-empt p.a.d. Conversation registration
        # at pad_conversation.Conversation.addcomment
        annotions[ANNOTATION_KEY] = aq_base(conversation)

    else:
        conversation = annotions[ANNOTATION_KEY]
    return conversation.__of__(content)


class StatusConversationReplies(pad_conversation.ConversationReplies):
    """An IReplies adapter for status conversations.

    This makes it easy to work with top-level comments.
    """
    implements(IReplies)
    # p.a.d. adapts class not interface, do the same
    adapts(StatusConversation)


# no need to also subclass CommentReplies - p.a.d. adapter is ok
