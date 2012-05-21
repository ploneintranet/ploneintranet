from zope.interface import alsoProvides
from zope.component import queryUtility

from AccessControl import getSecurityManager
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_inner
from Acquisition import aq_chain
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.common import ViewletBase

from z3c.form import form, field, button
from z3c.form.interfaces import IFormLayer
from plone.z3cform import z2
from plone.z3cform.fieldsets import extensible
from plone.z3cform.interfaces import IWrappedForm

from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog.statusupdate import StatusUpdate

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.microblog')


class StatusForm(extensible.ExtensibleForm, form.Form):

    ignoreContext = True  # don't use context to get widget data
    id = None
    label = _(u"Add a comment")
    fields = field.Fields(IStatusUpdate).omit('portal_type',
                                              '__parent__',
                                              '__name__',
                                              'id',
                                              'mime_type',
                                              'creator',
                                              'userid',
                                              'creation_date')

    def updateFields(self):
        super(StatusForm, self).updateFields()

    def updateWidgets(self):
        super(StatusForm, self).updateWidgets()

    def updateActions(self):
        super(StatusForm, self).updateActions()
        self.actions['cancel'].addClass("standalone")
        self.actions['cancel'].addClass("hide")
        self.actions['statusupdate'].addClass("context")

    @button.buttonAndHandler(_(u"add_statusupdate_button",
                               default=u"What are you doing?"),
                             name='statusupdate')
    def handleComment(self, action):

        # Validation form
        data, errors = self.extractData()
        if errors:
            return

        container = queryUtility(IMicroblogTool)
        status = StatusUpdate(data['text'])

        # debugging only
#        container.clear()

        # save the status update
        container.add(status)

        # Redirect to portal home
        self.request.response.redirect(self.action)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        # This method should never be called, it's only there to show
        # a cancel button that is handled by a jQuery method.
        pass  # pragma: no cover


class StatusViewlet(ViewletBase):

    form = StatusForm
    index = ViewPageTemplateFile('status.pt')

    comment_transform_message = "What's on your mind?"

    def __init__(self, compact, *args, **kwargs):
        super(StatusViewlet, self).__init__(*args, **kwargs)
        self.compact = compact
        # force microblog context to SiteRoot singleton
        for obj in aq_chain(self.context):
            if IPloneSiteRoot.providedBy(obj):
                self.context = obj
                return

    def update(self):
        super(StatusViewlet, self).update()
        if self.available:
            z2.switch_on(self, request_layer=IFormLayer)
            self.form = self.form(aq_inner(self.context), self.request)
            alsoProvides(self.form, IWrappedForm)
            self.form.update()

    @property
    def available(self):
        permission = "Plone Social: Add Microblog Status Update"
        return getSecurityManager().checkPermission(permission, self.context)
