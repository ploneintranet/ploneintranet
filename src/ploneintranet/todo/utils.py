from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


def update_task_status(self, return_status_message=False):
    """
    opens or closes tasks
    is used by workspace sidebar and dashboard
    """
    current_tasks = self.request.form.get('current-tasks', [])
    active_tasks = self.request.form.get('active-tasks', [])

    wft = api.portal.get_tool("portal_workflow")
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(UID={'query': current_tasks,
                          'operator': 'or'})
    for brain in brains:
        obj = brain.getObject()
        state = wft.getInfoFor(obj, 'review_state')
        if brain.UID in active_tasks:
            if state in ["open", "planned"]:
                api.content.transition(obj, "finish")
        else:
            if state == "done":
                obj.reopen()
        obj.reindexObject()

    if return_status_message:
        api.portal.show_message(
            _(u'Task state changed'), self.request, 'success')
        msg = ViewPageTemplateFile('browser/templates/globalstatusmessage.pt')
        return msg(self)
