from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.formlib.form import Fields
from zope.interface import implements


class IRosterPortlet(IPortletDataProvider):
    """
    Provides a button to participants which links to the roster view
    """


class Assignment(base.Assignment):

    implements(IRosterPortlet)

    @property
    def title(self):
        return u"Roster"


class Renderer(base.Renderer):

    render = ViewPageTemplateFile("templates/roster_portlet.pt")

    @property
    def available(self):
        return True

    def on_workspace(self):
        """
        are we within a workspace?
        """
        return getattr(self.context, 'acquire_workspace', None) is not None


class AddForm(base.AddForm):

    form_fields = Fields(IRosterPortlet)
    label = u"Add roster portlet"
    description = "This portlet gives participants access to the roster view"

    def create(self, data):
        return Assignment()


class EditForm(base.EditForm):

    form_fields = Fields(IRosterPortlet)
    label = "Edit roster portlet"
    description = "This portlet gives participants access to the roster view"
