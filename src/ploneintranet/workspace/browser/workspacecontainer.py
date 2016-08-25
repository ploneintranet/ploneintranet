# coding=utf-8
from Acquisition import aq_inner
from collections import defaultdict
from email.Utils import formatdate
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.tiles.workspaces import my_workspaces
from ploneintranet.workspace.config import TEMPLATES_FOLDER
from ploneintranet.workspace.interfaces import IMetroMap
from ploneintranet.workspace.workspacecontainer import IWorkspaceContainer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from time import time
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.schema.interfaces import IVocabularyFactory

vocab = 'ploneintranet.workspace.vocabularies.Divisions'


@implementer(Interface)
class BookmarkableWSDict(object):

    def __init__(self, ws_dict):
        ''' Transforms a dict in to a traversable object
        '''
        self.ws_dict = ws_dict

    def UID(self):
        return self.ws_dict['uid']

    def absolute_url(self):
        return self.ws_dict['url']


class Workspaces(BrowserView):
    """ A view to serve as overview over workspaces """

    _sorting_cookie = 'ploneintranet.workspace.my_workspace_sorting'
    _sorting_cookie_seconds = 30 * 86400  # 30 days

    def __call__(self):
        """Render the default template"""
        context = aq_inner(self.context)
        if IWorkspaceContainer.providedBy(context):
            self.target = context
        else:
            # hardcoded at the moment to fetch a folder called 'workspaces'
            self.target = getattr(context, 'workspaces')
        self.can_add = api.user.has_permission(
            'Add portal content',
            obj=self.target
        )
        if not api.user.is_anonymous():
            self.persist_sort_option()
        return super(Workspaces, self).__call__()

    def get_selected_sort_option(self):
        ''' This will return the selected sort option

        The rules are:

        1. Check the request
        2. Check the cookie
        3. Check the registry
        4. Default to "alphabet"
        '''
        requested_sort = self.request.get('sort')
        if requested_sort:
            return requested_sort
        requested_sort = self.request.get(self._sorting_cookie)
        if requested_sort:
            self.request.form['sort'] = requested_sort
            return requested_sort
        try:
            return api.portal.get_registry_record(
                'ploneintranet.workspace.my_workspace_sorting'
            )
        except api.exc.InvalidParameterError:
            # fallback if registry entry is not there
            return 'alphabet'

    @memoize
    def sort_options(self):
        options = [{'value': 'alphabet',
                    'content': _(u'Alphabetical')},
                   {'value': 'newest',
                    'content': _(u'Newest workspaces on top')},
                   # Not yet implemented
                   # {'value': 'activity',
                   #  'content': 'Most active workspaces on top'}
                   ]
        return options

    def persist_sort_option(self):
        ''' This will persist the selected sort option in to a cookie
        '''
        option = self.get_selected_sort_option()

        # if its already equal to the cookie don't do nothing
        if option == self.request.get(self._sorting_cookie):
            return

        # otherwise check that it is a valid option
        for valid_option in self.sort_options():
            if valid_option['value'] == option:
                # if it is set the cookie and return
                expiration_seconds = time() + self._sorting_cookie_seconds
                expires = formatdate(expiration_seconds, usegmt=True)
                return self.request.response.setCookie(
                    self._sorting_cookie,
                    option,
                    expires=expires
                )

    def grouping_options(self):
        options = [{'value': '',
                    'content': _(u'No grouping')},
                   {'value': 'division',
                    'content': _(u'Group by division')},
                   # Not yet implemented
                   # {'value': 'workspace_type',
                   #  'content': 'Group by workspace type'}
                   ]
        return options

    def get_bookmark_link(self, ws_dict):
        ''' Get's the workspace bookmark icon from the dictionary
        '''
        obj = BookmarkableWSDict(ws_dict)
        view = api.content.get_view(
            'bookmark-link-iconified',
            obj,
            self.request
        )
        return view()

    def workspace_types(self):
        options = [{'value': '', 'content': _(u'All workspace types')}]
        translate = self.context.translate
        try:
            additional_filters = api.portal.get_registry_record(
                'ploneintranet.workspace.workspace_type_filters')
            # Sort them by the translated values
            for portal_type in sorted(
                    additional_filters,
                    key=lambda x: translate(_(additional_filters.get(x))),
            ):
                label = additional_filters[portal_type]
                options.append({'value': portal_type, 'content': _(label)})
        except api.exc.InvalidParameterError:
            # fallback if registry entry is not there
            options.extend([
                {'value': 'ploneintranet.workspace.workspacefolder',
                 'content': _(u'Generic workspaces')},
                {'value': 'ploneintranet.workspace.case',
                 'content': _(u'Cases')},
            ])
        return options

    def workspaces_by_division(self):
        ''' returns workspaces grouped by division
        '''
        workspaces = my_workspaces(self.context,
                                   self.request,
                                   include_activities=False)
        self.divisions = getUtility(IVocabularyFactory, vocab)(self.context)
        division_uids = [x.value for x in self.divisions]
        division_map = defaultdict(list)
        for workspace in workspaces:
            # Note: Already sorted as source list is sorted
            if workspace['uid'] in division_uids:
                division_map[workspace['uid']].append(workspace)
            else:
                division_map[workspace['division']].append(workspace)

        return division_map

    @memoize
    def workspaces(self):
        ''' The list of my workspaces
        '''
        return my_workspaces(self.context,
                             self.request,
                             include_activities=False)


class AddView(BrowserView):
    """ Add Form in a modal to create a new workspace """

    TEMPLATES_FOLDER = TEMPLATES_FOLDER
    types_with_policy = (
        'ploneintranet.workspace.workspacefolder',
    )

    def workflows(self):
        return IMetroMap(self.context).get_available_metromap_workflows()

    @memoize
    def get_addable_types(self):
        ''' List the content that are addable in this context
        '''
        types = self.get_templates_by_type().keys()
        if 'ploneintranet.workspace.workspacefolder' not in types:
            types.append('ploneintranet.workspace.workspacefolder')
        ftis = self.context.allowedContentTypes()
        selected_fti = self.request.get(
            'portal_type',
            self.default_fti
        )
        addable_types = [
            {
                'id': fti.getId(),
                'title': fti.Title(),
                'selected': fti.getId() == selected_fti and 'selected' or None,
            }
            for fti in ftis if fti.getId() in types
        ]
        addable_types.sort(key=lambda x: x['title'])
        return addable_types

    @memoize
    def get_fti_titles_by_type(self):
        ''' Get's the titles of the fti by portal_type as a dictionary
        '''
        return {
            x['id']: x['title']
            for x in self.get_addable_types()
        }

    @memoize
    def get_templates_by_type(self):
        """
        Return a list of Cases in the templates folder which the current user
        has the rights to view. Templates may only be relevant to particular
        groups or users.
        """
        templates_by_type = defaultdict(list)
        portal = api.portal.get()
        templates = portal.get(TEMPLATES_FOLDER).getFolderContents()
        for template in templates:
            templates_by_type[template['portal_type']].append(
                {
                    'id': template['getId'],
                    'title': template['Title'],
                    'portal_type': template['portal_type'],
                    'description': template['Description'],
                }
            )
        return templates_by_type

    def divisions(self):
        divisions = getUtility(IVocabularyFactory, vocab)(self.context)
        return divisions


class WorkspaceTabsTile(Tile):

    index = ViewPageTemplateFile("tiles/templates/workspace-tabs-tile.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
