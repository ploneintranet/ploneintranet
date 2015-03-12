from zope.interface import implements
from zope.component import getMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from plone.app.layout.globals.interfaces import IViewView
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ploneintranet.core.integration import PLONESOCIAL

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('ploneintranet.activitystream')


class StatusConversationView(BrowserView):
    """Standalone view wrapping statusconversation_provider
    """

    implements(IPublishTraverse, IViewView)

    index = ViewPageTemplateFile("templates/conversation.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.status_id = None
        self.thread_id = None

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def update(self):
        """Mute plone.app.z3cform.kss.validation AttributeError"""
        pass

    def publishTraverse(self, request, name):
        """ used for traversal via publisher, i.e. when using as a url """
        self.status_id = long(name)
        return self

    @property
    def title(self):
        return _("Conversation")

    def statusconversation_provider(self):
        container = PLONESOCIAL.microblog
        if not PLONESOCIAL.microblog or not self.status_id:
            return ''

        status = container.get(self.status_id)
        if not status:
            return 'invalid status_id: %s' % self.status_id

        provider = getMultiAdapter(
            (status, self.request, self),
            name="ploneintranet.activitystream.statusconversation_provider")
        return provider()
