# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from plone.tiles import Tile
from plone import api
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from zope.component import getUtility
from zope.component import queryUtility
from ploneintranet.layout.utils import shorten


class WorkspacesTile(Tile):

    index = ViewPageTemplateFile("templates/workspaces.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    @property
    def workspace_type(self):
        """
        A tile should show either Workspacefolders or Cases, not both.
        """
        return self.request.form.get(
            'workspace_type',
            ['ploneintranet.workspace.workspacefolder',
             'ploneintranet.workspace.case'])

    def shorten(self, text):
        return shorten(text, length=60)

    @memoize
    def workspaces(self, include_activities=False):
        """ The list of my workspaces
        """
        return my_workspaces(self.context, workspace_types=self.workspace_type,
                             include_activities=include_activities)


def my_workspaces(context,
                  request={},
                  workspace_types=[],
                  include_activities=True):
    """ The list of my workspaces
    Is also used in theme/browser/workspace.py view.

    To get the sorting method:

    1. Check the request
    2. Check the registry
    3. Default to "alphabet"
    """
    sort_option = request.get('sort', '')
    if not sort_option:
        try:
            sort_option = api.portal.get_registry_record(
                'ploneintranet.workspace.my_workspace_sorting'
            )
        except api.exc.InvalidParameterError:
            # fallback if registry entry is not there
            sort_option = u'alphabet'

    if sort_option == "activity":
        raise NotImplementedError(
            "Sorting by activity"
            "is not yet possible")
    elif sort_option == "newest":
        sort_by = "modified"
    elif sort_option == "alphabet":
        sort_by = "sortable_title"
    else:
        sort_by = "sortable_title"

    # The rule to get the workspace types is this one
    #
    # 1. Look in to the request
    # 2. Use the function parameter
    # 3. Check if we have something in the registry
    # 4. Use a default for backward compatibility
    workspace_types = request.get('workspace_type', []) or workspace_types
    if not workspace_types:
        try:
            workspace_types = list(
                api.portal.get_registry_record(
                    'ploneintranet.workspace.workspace_types'
                )
            )
        except api.exc.InvalidParameterError:
            workspace_types = [
                'ploneintranet.workspace.case',
                'ploneintranet.workspace.workspacefolder',
            ]

    searchable_text = request.get('SearchableText', '').strip()
    ws_path = "/".join(context.getPhysicalPath())

    query = dict(
        portal_type=workspace_types,
        path=ws_path
    )

    sitesearch = getUtility(ISiteSearch)
    if searchable_text:
        response = sitesearch.query(phrase=searchable_text,
                                    filters=query,
                                    step=99999)
    else:
        response = sitesearch.query(filters=query, step=99999)

    portal = api.portal.get()
    workspaces = []

    try:
        workspace_types_css_mapping = api.portal.get_registry_record(
            'ploneintranet.workspace.workspace_types_css_mapping'
        )
    except api.exc.InvalidParameterError:
        # backward compatibility
        workspace_types_css_mapping = [
            'ploneintranet.workspace.case|type-case'
        ]

    css_mapping = {}
    for line in workspace_types_css_mapping:
        key, value = line.partition('|')[::2]
        css_mapping[key] = value

    for item in response:
        path_components = item.path.split('/')
        item_id = path_components[-1]
        css_class = " ".join((
            escape_id_to_class(item_id),
            css_mapping.get(item.portal_type, ''),
        ))

        activities = []
        if include_activities:
            obj = portal.restrictedTraverse(path_components)
            activities = get_workspace_activities(obj)

        workspaces.append({
            'id': item_id,
            'uid': item.context['UID'],
            'title': item.title,
            'description': item.description,
            'url': item.url,
            'activities': activities,
            'class': css_class,
            'modified': item.modified,
            'division': item.context.get('division', '')
        })

    if sort_by == 'modified':
        workspaces.sort(key=lambda item: item['modified'], reverse=True)
    else:
        workspaces.sort(key=lambda item: item['title'].lower())
    return workspaces


def get_workspace_activities(obj, limit=1):
    """ Return the workspace activities sorted by reverse chronological
    order

    Regarding the time value:
     - the datetime value contains the time in international format
       (machine readable)
     - the title value contains the absolute date and time of the post
    """
    mb = queryUtility(IMicroblogTool)
    items = mb.context_values(obj, limit=limit)
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
