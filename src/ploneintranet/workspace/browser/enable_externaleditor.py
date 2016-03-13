from collective.externaleditor.browser.views import ExternalEditView
from collective.externaleditor.browser.views import ExternalEditorEnabledView
from plone import api


def always_activated():
    return api.portal.get_registry_record(
        'ploneintranet.workspace.externaleditor_always_activated')


class EnabledView(ExternalEditorEnabledView):
    """
    Display the link to the external editor in the interface.
    """
    def isActivatedInMemberProperty(self):
        if always_activated():
            return True
        else:
            return super(EnabledView, self).isActivatedInMemberProperty()

    def isActivatedInSiteProperty(self):
        if always_activated():
            return True
        else:
            return super(EnabledView, self).isActivatedInSiteProperty()


class EditView(ExternalEditView):
    """
    Return the object for editing.
    """

    def isActivatedInMemberProperty(self):
        if always_activated():
            return True
        else:
            return super(EditView, self).isActivatedInMemberProperty()

    def isActivatedInSiteProperty(self):
        if always_activated():
            return True
        else:
            return super(EditView, self).isActivatedInSiteProperty()
