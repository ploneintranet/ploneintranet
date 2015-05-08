from datetime import datetime

from AccessControl import Unauthorized
from plone import api
from plone.app.contenttypes.interfaces import IEvent
from plone.memoize.instance import memoize
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.publisher.browser import BrowserView

from ...utils import TYPE_MAP
from ...utils import parent_workspace
from ...utils import existing_users
from ...policies import EXTERNAL_VISIBILITY
from ...policies import JOIN_POLICY
from ...policies import PARTICIPANT_POLICY
from ... import MessageFactory as _
from ploneintranet.todo.behaviors import ITodo


FOLDERISH_TYPES = ['Folder']
BLACKLISTED_TYPES = ['Event', 'simpletodo']


class BaseTile(BrowserView):

    index = None
    form_submitted = False

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def workspace(self):
        """ Acquire the workspace of the current context
        """
        return parent_workspace(self)

    def can_manage_workspace(self):
        """
        does this user have permission to manage the workspace
        """
        return api.user.has_permission(
            "ploneintranet.workspace: Manage workspace",
            obj=self,
        )


class SidebarSettingsMembers(BaseTile):
    """ A view to serve as the member roster in the sidebar
    """

    index = ViewPageTemplateFile('templates/sidebar-settings-members.pt')

    def users(self):
        """Get current users and add in any search results.

        :returns: a list of dicts with keys
         - id
         - title
        :rtype: list
        """
        existing_users = self.existing_users()
        existing_user_ids = [x['id'] for x in existing_users]

        # Only add search results that are not already members
        sharing = getMultiAdapter((self.workspace(), self.request),
                                  name='sharing')
        search_results = sharing.user_search_results()
        users = existing_users + [x for x in search_results
                                  if x['id'] not in existing_user_ids]

        users.sort(key=lambda x: safe_unicode(x['title']))
        return users

    @memoize
    def existing_users(self):
        return existing_users(self.workspace())


class SidebarSettingsSecurity(BaseTile):
    """ A view to serve as the security settings in the sidebar
    """

    index = ViewPageTemplateFile('templates/sidebar-settings-security.pt')

    def __init__(self, context, request):
        """ set up local copies of the policies for the sidebar template
        """
        super(SidebarSettingsSecurity, self).__init__(context, request)
        self.external_visibility = EXTERNAL_VISIBILITY
        self.join_policy = JOIN_POLICY
        self.participant_policy = PARTICIPANT_POLICY

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form
        ws = self.workspace()

        def update_field(field_name):
            index = int(form.get(field_name)) - 1
            field = getattr(self, field_name)
            value = field.keys()[index]

            if value != getattr(ws, field_name):
                if field_name == 'external_visibility':
                    ws.set_external_visibility(value)
                else:
                    setattr(ws, field_name, value)
                api.portal.show_message(
                    _(u'Workspace security policy changes saved'),
                    self.request,
                    'success',
                )

        if self.request.method == 'POST':
            if not self.can_manage_workspace():
                msg = _(u'You do not have permission to change the workspace '
                        u'policy')
                raise Unauthorized(msg)
            if form:
                for field in [
                    'external_visibility', 'join_policy', 'participant_policy'
                ]:
                    update_field(field)

        return self.render()


class SidebarSettingsAdvanced(BaseTile):
    """ A view to serve as the advanced config in the sidebar
    """

    index = ViewPageTemplateFile('templates/sidebar-settings-advanced.pt')

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form
        ws = self.workspace()

        if self.request.method == 'POST':
            if not self.can_manage_workspace():
                msg = _(u'You do not have permission to change the workspace '
                        u'policy')
                raise Unauthorized(msg)
            if form.get('email') and form.get('email') != ws.email:
                ws.email = form.get('email').strip()
                api.portal.show_message(_(u'Email changed'),
                                        self.request,
                                        'success')
                self.form_submitted = True

        return self.render()


class Sidebar(BaseTile):

    """ A view to serve as a sidebar navigation for workspaces
    """

    index = ViewPageTemplateFile('templates/sidebar.pt')

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form
        ws = self.workspace()

        if self.request.method == 'POST':
            if not self.can_manage_workspace():
                msg = _(u'You do not have permission to change the workspace '
                        u'title or description')
                raise Unauthorized(msg)
            if self.request.form.get('section', None) == 'task':
                current_tasks = self.request.form.get('current-tasks', [])
                active_tasks = self.request.form.get('active-tasks', [])

                catalog = api.portal.get_tool('portal_catalog')
                brains = catalog(UID={'query': current_tasks,
                                      'operator': 'or'})
                for brain in brains:
                    obj = brain.getObject()
                    todo = ITodo(obj)
                    if brain.UID in active_tasks:
                        todo.status = u'done'
                    else:
                        todo.status = u'tbd'
                api.portal.show_message(_(u'Changes applied'),
                                        self.request,
                                        'success')
            else:
                if form.get('title') and form.get('title') != ws.title:
                    ws.title = form.get('title').strip()
                    api.portal.show_message(_(u'Title changed'),
                                            self.request,
                                            'success')

                if form.get('description') and \
                   form.get('description') != ws.description:
                    ws.description = form.get('description').strip()
                    api.portal.show_message(_(u'Description changed'),
                                            self.request,
                                            'success')

                calendar_visible = not not form.get('calendar_visible')
                if calendar_visible != ws.calendar_visible:
                    ws.calendar_visible = calendar_visible
                    api.portal.show_message(_(u'Calendar visibility changed'),
                                            self.request,
                                            'success')

        return self.render()

    # ContentItems

    def parent(self):
        if (self.context.portal_type ==
                'ploneintranet.workspace.workspacefolder'):
            return None
        parent = self.context.aq_parent
        return {'id': parent.getId(),
                'title': parent.Title(),
                'url': parent.absolute_url() + '/@@sidebar.default'}

    def children(self):
        """ returns a list of dicts of items in the current context
        """
        items = []
        catalog = self.context.portal_catalog
        current_path = '/'.join(self.context.getPhysicalPath())

        sidebar_search = self.request.get('sidebar-search', None)
        query = {}
        allowed_types = [i for i in api.portal.get_tool('portal_types')
                         if i not in BLACKLISTED_TYPES]
        query['portal_type'] = allowed_types
        if sidebar_search:
            # XXX plone only allows * as postfix.
            query['SearchableText'] = '%s*' % sidebar_search
            query['path'] = current_path
            # With solr we might want to do real substr
            results = catalog.searchResults(query)
        else:
            query['sort_on'] = 'sortable_title'
            results = self.context.getFolderContents(query)

        for item in results:
            portal_type = item['portal_type']
            if portal_type in BLACKLISTED_TYPES:
                continue

            # Do some checks to set the right classes for icons and candy
            desc = (
                'has-description' if item['Description']
                else 'has-no-description'
            )

            # XXX: will be needed later for grouping by mimetyp
            mime_type = ''
            # typ can be user, folder, date and mime-typish
            typ = TYPE_MAP.get(portal_type, 'none')
            url = item.getURL()

            ptool = api.portal.get_tool('portal_properties')
            view_action_types = \
                ptool.site_properties.typesUseViewActionInListings

            if portal_type in FOLDERISH_TYPES:
                dpi = (
                    'source: #workspace-documents; '
                    'target: #workspace-documents; '
                    'url: %s/@@sidebar.default#workspace-documents' % url
                )
                content_type = 'group'
            else:
                if portal_type in view_action_types:
                    url = '%s/view' % url
                dpi = (
                    'target: #document-body; '
                    'source: #document-body; '
                    'history: record'
                )
                content_type = 'document'

            cls = 'item %s type-%s %s' % (content_type, typ, desc)

            items.append({
                'id': item['getId'],
                'cls': cls,
                'title': item['Title'],
                'description': item['Description'],
                'url': url,
                'type': TYPE_MAP.get(item['portal_type'], 'none'),
                'mime-type': mime_type,
                'dpi': dpi})
        return items

    def tasks(self):
        items = []
        catalog = api.portal.get_tool('portal_catalog')
        current_path = '/'.join(self.context.getPhysicalPath())
        ptype = 'simpletodo'
        brains = catalog(path=current_path, portal_type=ptype)
        for brain in brains:
            obj = brain.getObject()
            todo = ITodo(obj)
            data = {
                'id': brain.UID,
                'title': brain.Description,
                'content': brain.Title,
                'url': brain.getURL(),
                'checked': todo.status == u'done'
            }
            items.append(data)
        return items

    def events(self):
        catalog = api.portal.get_tool('portal_catalog')
        workspace = parent_workspace(self.context)
        workspace_path = '/'.join(workspace.getPhysicalPath())
        now = datetime.now()

        # Current and future events
        upcoming_events = catalog.searchResults(
            object_provides=IEvent.__identifier__,
            path=workspace_path,
            start={'query': (now), 'range': 'min'},
        )

        # Events which have finished
        older_events = catalog.searchResults(
            object_provides=IEvent.__identifier__,
            path=workspace_path,
            end={'query': (now), 'range': 'max'},
        )
        return {'upcoming': upcoming_events, 'older': older_events}
