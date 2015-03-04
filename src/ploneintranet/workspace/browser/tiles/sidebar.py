# from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet.workspace.utils import TYPE_MAP
from ploneintranet.workspace.utils import parent_workspace
from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from plone import api
from plone.i18n.normalizer import idnormalizer
from collective.workspace.interfaces import IWorkspace
from plone.app.contenttypes.interfaces import IEvent
from plone.memoize.instance import memoize
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import _checkPermission as checkPermission
from ploneintranet.todo.behaviors import ITodo
from Products.statusmessages.interfaces import IStatusMessage
from ploneintranet.workspace import MessageFactory as _

FOLDERISH_TYPES = ['folder']


class BaseTile(BrowserView):

    index = None

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def status_messages(self):
        """ Returns status messages if any
        """
        messages = IStatusMessage(self.request)
        m = messages.show()
        for item in m:
            item.id = idnormalizer.normalize(item.message)
        return m

    def my_workspace(self):
        return parent_workspace(self)


class SidebarSettingsMembers(BaseTile):
    """ A view to serve as the member roster in the sidebar
    """

    index = ViewPageTemplateFile("templates/sidebar-settings-members.pt")

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
        sharing = getMultiAdapter((self.my_workspace(), self.request),
                                  name='sharing')
        search_results = sharing.user_search_results()
        users = existing_users + [x for x in search_results
                                  if x['id'] not in existing_user_ids]

        users.sort(key=lambda x: safe_unicode(x["title"]))
        return users

    def my_workspace(self):
        return parent_workspace(self)

    @memoize
    def existing_users(self):

        members = IWorkspace(self.my_workspace()).members
        info = []
        portal = api.portal.get()

        for userid, details in members.items():
            user = api.user.get(userid)
            if user is None:
                continue
            user = user.getUser()
            title = user.getProperty('fullname') or user.getId() or userid
            # XXX tbd, we don't know what a persons description is, yet
            description = _(u'Here we could have a nice status of this person')
            classes = description and 'has-description' or 'has-no-description'
            portrait = '%s/portal_memberdata/portraits/%s' % \
                       (portal.absolute_url(), userid)

            info.append(
                dict(
                    id=userid,
                    title=title,
                    description=description,
                    portrait=portrait,
                    cls=classes,
                    member=True,
                    admin='Admins' in details['groups'],
                )
            )

        return info

    def can_manage_workspace(self):
        """
        does this user have permission to manage the workspace
        """
        return checkPermission(
            "ploneintranet.workspace: Manage workspace",
            self.context,
        )


class SidebarSettingsSecurity(BaseTile):
    """ A view to serve as the security settings in the sidebar
    """

    index = ViewPageTemplateFile("templates/sidebar-settings-security.pt")


class SidebarSettingsAdvanced(BaseTile):
    """ A view to serve as the advanced config in the sidebar
    """

    index = ViewPageTemplateFile("templates/sidebar-settings-advanced.pt")

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form

        if self.request.method == "POST" and form:
            ws = self.my_workspace()

            if form.get('email') and form.get('email') != ws.email:
                ws.email = form.get('email').strip()
                api.portal.show_message(_(u'Email changed'),
                                        self.request,
                                        'success')

        return self.render()


class Sidebar(BaseTile):

    """ A view to serve as a sidebar navigation for workspaces
    """

    index = ViewPageTemplateFile("templates/sidebar.pt")

    def __call__(self):
        """ write attributes, if any, set state, render
        """
        form = self.request.form

        if self.request.method == "POST" and form:
            ws = self.my_workspace()
            if self.request.form.get('section', None) == 'task':
                current_tasks = self.request.form.get('current-tasks', [])
                active_tasks = self.request.form.get('active-tasks', [])

                catalog = api.portal.get_tool("portal_catalog")
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

                workspace_visible = not not form.get('workspace_visible')
                if workspace_visible != ws.workspace_visible:
                    ws.workspace_visible = workspace_visible
                    api.portal.show_message(_(u'Workspace visibility changed'),
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
        if self.context.portal_type == \
                "ploneintranet.workspace.workspacefolder":
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
        if sidebar_search:
            st = '%s*' % sidebar_search  # XXX plone only allows * as postfix.
            # With solr we might want to do real substr
            results = catalog.searchResults(SearchableText=st,
                                            path=current_path)
        else:
            results = self.context.getFolderContents()

        for item in results:
            # Do some checks to set the right classes for icons and candy
            desc = (
                item['Description']
                and 'has-description'
                or 'has-no-description'
            )

            content_type = TYPE_MAP.get(item['portal_type'], 'none')

            mime_type = ''  # XXX: will be needed later for grouping by mimetyp
            # typ can be user, folder, date and mime typish
            typ = 'folder'  # XXX: This needs to get dynamic later

            if content_type in FOLDERISH_TYPES:
                dpi = (
                    "source: #workspace-documents; "
                    "target: #workspace-documents"
                )
                url = item.getURL() + '/@@sidebar.default#workspace-documents'
                content_type = 'group'
            else:
                dpi = "target: #document-body"
                url = item.getURL() + "#document-body"
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
        catalog = api.portal.get_tool("portal_catalog")
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
        catalog = api.portal.get_tool("portal_catalog")
        workspace = parent_workspace(self.context)
        workspace_path = '/'.join(workspace.getPhysicalPath())
        now = DateTime()

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
        return {"upcoming": upcoming_events, "older": older_events}
