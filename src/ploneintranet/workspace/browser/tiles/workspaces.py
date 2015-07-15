# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from plone.tiles import Tile
from plone import api
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from zope.component import queryUtility


class WorkspacesTile(Tile):

    index = ViewPageTemplateFile("templates/workspaces.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    @memoize
    def workspaces(self):
        """ The list of my workspaces
        """
        return my_workspaces(self.context)


def my_workspaces(context, request=None):
    """ The list of my workspaces
    Is also used in theme/browser/workspace.py view.
    """

    # determine sorting order (default: alphabetical)
    sort_by = "sortable_title"
    order = "ascending"
    if request:
        if hasattr(request, "sort"):
            if request.sort == "activity":
                raise NotImplementedError(
                    "Sorting by activity"
                    "is not yet possible")
            elif request.sort == "newest":
                sort_by = "modified"
                order = "reverse"

    pc = api.portal.get_tool('portal_catalog')
    portal = api.portal.get()
    ws_folder = portal.get("workspaces")
    ws_path = "/".join(ws_folder.getPhysicalPath())
    brains = pc(
        object_provides=(
            'ploneintranet.workspace.workspacefolder.IWorkspaceFolder'),
        portal_type=["ploneintranet.workspace.workspacefolder",
                     "ploneintranet.workspace.case"],
        sort_on=sort_by,
        sort_order=order,
        path=ws_path,
    )
    workspaces = []
    for brain in brains:
        css_class = escape_id_to_class(brain.getId)
        if brain.portal_type == 'ploneintranet.workspace.case':
            css_class = 'type-case ' + css_class
        workspaces.append({
            'id': brain.getId,
            'title': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'activities': get_workspace_activities(brain),
            'class': css_class,
        })
    return workspaces


def get_workspace_activities(brain, limit=1):
    """ Return the workspace activities sorted by reverse chronological
    order

    Regarding the time value:
     - the datetime value contains the time in international format
       (machine readable)
     - the title value contains the absolute date and time of the post
    """
    mb = queryUtility(IMicroblogTool)
    items = mb.context_values(brain.getObject(), limit=limit)
    mtool = api.portal.get_tool('portal_membership')
    results = []
    for item in items:
        user_data = mtool.getMemberInfo(item.creator)
        creator = user_data.get('fullname') if user_data else item.creator
        results.append(dict(
            subject=creator,
            verb=_(u'posted'),
            object=item.text,
            time={
                'datetime': item.date.strftime('%Y-%m-%d'),
                'title': item.date.strftime('%d %B %Y, %H:%M')}
        ))
    return results


def escape_id_to_class(cid):
    """ We use workspace ids as classes to style them.
        if a workspace has dots in its name, this is not usable as a class
        name. We have to escape that. We might need to do more to them, so this
        became a utility function.
    """
    return cid.replace('.', '-')
