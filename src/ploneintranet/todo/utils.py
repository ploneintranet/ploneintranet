from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


def update_task_status(self, return_status_message=False):
    """
    opens or closes tasks
    is used by workspace sidebar and dashboard
    Since tasks that are checked (in the sidebar), but marked as disabled (when
    the user does not have the permission to change the workflow) are not
    present in the request, we must keep a separate hidden-input list of tasks
    that are actually checked, but disabled.
    Also, we must keep a list of checked and not disabled tasks, so that we
    can detect if one of them was un-checked by the user and therefore needs
    to be reopened.
    """
    current_tasks = self.request.form.get('current-tasks', [])
    active_tasks = set(self.request.form.get('active-tasks', []))
    disabled_checked_tasks = set(self.request.form.get(
        'disabled-checked-tasks', []))
    # Active tasks: those that are present, via checkbox, in the request,
    # plus those that are marked via hidden input as checked but disabled.
    all_active_tasks = active_tasks.union(disabled_checked_tasks)

    checked_tasks = set(self.request.form.get('checked-tasks', []))
    # All tasks which until now had been checked and enabled, but are no longer
    # present in the request, need to be re-opened.
    reopen_tasks = checked_tasks.difference(active_tasks)

    wft = api.portal.get_tool("portal_workflow")
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(UID={'query': current_tasks,
                          'operator': 'or'})

    for brain in brains:
        obj = brain.getObject()
        state = wft.getInfoFor(obj, 'review_state')
        if brain.UID in all_active_tasks:
            if state in ["open", "planned"]:

                api.content.transition(obj, "finish")
                obj.reindexObject()
        if brain.UID in reopen_tasks:
            if state == "done":
                obj.reopen()
                obj.reindexObject()

    if return_status_message:
        api.portal.show_message(
            _(u'Task state changed'), self.request, 'success')
        msg = ViewPageTemplateFile('browser/templates/globalstatusmessage.pt')
        return msg(self)
