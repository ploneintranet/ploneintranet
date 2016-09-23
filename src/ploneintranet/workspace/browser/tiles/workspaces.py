# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.tiles import Tile
from plone import api
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.core import ploneintranetCoreMessageFactory as _
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


class WorkspaceTile(Tile):
    index = ViewPageTemplateFile("templates/workspace.tile.pt")

    @property
    @memoize_contextless
    def plone_view(self):
        ''' The plone_view called in the context of the portal
        '''
        return api.content.get_view(
            'plone',
            api.portal.get(),
            self.request,
        )

    @property
    @memoize_contextless
    def workspace_type_mapping(self):
        ''' Return the mapping between workspace types and css types
        as defined in the registry record
        ploneintranet.workspace.workspace_types_css_mapping
        '''
        try:
            workspace_types_css_mapping = api.portal.get_registry_record(
                'ploneintranet.workspace.workspace_types_css_mapping'
            )
        except api.exc.InvalidParameterError:
            # backward compatibility
            workspace_types_css_mapping = [
                'ploneintranet.workspace.case|type-case'
            ]

        css_mapping = dict(
            line.partition('|')[::2]
            for line in workspace_types_css_mapping
        )
        return css_mapping

    @property
    def workspace_type(self):
        ''' Return, if found the workspace type mapping
        '''
        return self.workspace_type_mapping.get(
            self.context.portal_type, 'workspace'
        )

    def get_css_classes(self):
        ''' Return the css classes for this tile
        '''
        classes = [
            'workspace-' + self.context.id.replace('.', '-'),
            getattr(self.context, 'class', ''),
            self.workspace_type,
        ]
        if (
            getattr(self.context, 'is_archived', False) or
            getattr(self.context, 'archival_date', False)
        ):
            classes.append('state-archived')
        return ' '.join(classes)


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

    # The rule to get the workspace types is this one
    #
    # 1. Look in to the request
    # 2. Use the function parameter
    # 3. Check if we have something in the registry
    # 4. Use a default for backward compatibility
    workspace_types = request.get('workspace_type', []) or workspace_types
    if not workspace_types:
        try:
            workspace_type_filters = api.portal.get_registry_record(
                'ploneintranet.workspace.workspace_type_filters')
            workspace_types = workspace_type_filters.keys()
        except api.exc.InvalidParameterError:
            workspace_types = [
                'ploneintranet.workspace.case',
                'ploneintranet.workspace.workspacefolder',
            ]

    searchable_text = request.get('SearchableText', '').strip()
    ws_path = "/".join(context.getPhysicalPath())

    query = dict(
        portal_type=workspace_types,
        path=ws_path,
    )

    include_archived = request.get('archived', False)
    if not include_archived:
        query['is_archived'] = False

    sitesearch = getUtility(ISiteSearch)
    if searchable_text:
        response = sitesearch.query(phrase=searchable_text,
                                    filters=query,
                                    step=99999)
    else:
        response = sitesearch.query(filters=query, step=99999)

    portal = api.portal.get()
    workspaces = []

    for item in response:
        path_components = item.path.split('/')
        item_id = path_components[-1]

        activities = []
        if include_activities:
            obj = portal.restrictedTraverse(path_components)
            activities = get_workspace_activities(obj)
        if activities:
            last_activity = max(
                activity.get('time', {}).get('timestamp', None)
                for activity in activities
            )
        else:
            last_activity = ''

        workspaces.append({
            'id': item_id,
            'uid': item.context['UID'],
            'title': item.title,
            'description': item.description,
            'url': item.url,
            'activities': activities,
            'modified': item.modified,
            'division': item.context.get('division', ''),
            'is_archived': item.is_archived,
            'archival_date': item.archival_date,
            'last_activity': last_activity,
            'portal_type': item.portal_type,
        })

    if sort_option == 'activity':
        workspaces.sort(key=lambda item: item['last_activity'], reverse=True)
    elif sort_option == 'newest':
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
                'title': item.date.strftime('%d %B %Y, %H:%M'),
                'timestamp': item.date.strftime('%s'),
            }
        ))
    return results
