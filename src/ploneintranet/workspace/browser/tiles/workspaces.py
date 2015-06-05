# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from plone.tiles import Tile
from plone import api
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from zope.component import queryUtility
from zExceptions import Unauthorized

import arrow


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

    def relative_date(self, date):
        lang = self.request.get('LANGUAGE', 'en')
        arrow_date = arrow.get(date)
        relative_date = arrow_date.humanize(locale=lang)
        return relative_date


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
    workspaces = []
    for brain in brains:
        try:
            workspaces.append({
                'id': brain.getId,
                'title': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'activities': get_workspace_activities(brain),
                'class': escape_id_to_class(brain.getId),
            })
        except Unauthorized:
            # the query above should actually filter on *my* workspaces
            # i.e. workspaces I'm a member of. This is just a stopgap
            pass
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
            date=item.date,
        ))
    return results


def escape_id_to_class(cid):
    """ We use workspace ids as classes to style them.
        if a workspace has dots in its name, this is not usable as a class
        name. We have to escape that. We might need to do more to them, so this
        became a utility function.
    """
    return cid.replace('.', '-')
