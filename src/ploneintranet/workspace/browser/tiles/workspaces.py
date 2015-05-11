# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from plone.tiles import Tile
from plone import api
from ploneintranet.microblog.interfaces import IMicroblogTool
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


def my_workspaces(context):
    """ The list of my workspaces
    Is also used in theme/browser/workspace.py view.
    """
    pc = api.portal.get_tool('portal_catalog')
    brains = pc(
        portal_type="ploneintranet.workspace.workspacefolder",
        sort_on="modified",
        sort_order="reversed",
    )
    workspaces = [
        {
            'id': brain.getId,
            'title': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'activities': get_workspace_activities(brain),
            'class': escape_id_to_class(brain.getId),
        } for brain in brains
    ]
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
            verb='posted',
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
