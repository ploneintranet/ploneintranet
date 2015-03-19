# from plone import api
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet.workspace import utils
from ploneintranet.workspace.policies import EXTERNAL_VISIBILITY
from ploneintranet.workspace.policies import JOIN_POLICY
from ploneintranet.workspace.policies import PARTICIPANT_POLICY
from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from plone import api
from plone.i18n.normalizer import idnormalizer
from plone.app.contenttypes.interfaces import IEvent
from ploneintranet.workspace import MessageFactory as _
from ploneintranet.workspace import config
from ploneintranet.workspace.interfaces import IGroupingStorage
from plone.memoize.instance import memoize
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import _checkPermission as checkPermission
from ploneintranet.todo.behaviors import ITodo
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getAdapter
from zope.component.interfaces import ComponentLookupError
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory

import logging

log = logging.getLogger(__name__)


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
        return utils.parent_workspace(self)


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

    @memoize
    def existing_users(self):
        return utils.existing_users(self.my_workspace())

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

        ws = self.my_workspace()

        def update_field(field_name):
            index = int(form.get(field_name)) - 1
            field = getattr(self, field_name)
            value = field.keys()[index]

            if value != getattr(ws, field_name):
                if field_name == "external_visibility":
                    ws.set_external_visibility(value)
                else:
                    setattr(ws, field_name, value)
                api.portal.show_message(
                    _(u'Workspace security policy changes saved'),
                    self.request,
                    'success',
                )

        if self.request.method == "POST" and form:
            for field in [
                'external_visibility', 'join_policy', 'participant_policy'
            ]:
                update_field(field)

        return self.render()


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

            content_type = utils.TYPE_MAP.get(item['portal_type'], 'none')

            mime_type = ''  # XXX: will be needed later for grouping by mimetyp
            # typ can be user, folder, date and mime typish
            typ = 'folder'  # XXX: This needs to get dynamic later
            url = item.getURL()

            ptool = api.portal.get_tool('portal_properties')
            view_action_types = \
                ptool.site_properties.typesUseViewActionInListings

            if content_type in FOLDERISH_TYPES:
                dpi = (
                    "source: #workspace-documents; "
                    "target: #workspace-documents"
                )
                url = url + '/@@sidebar.default#workspace-documents'
                content_type = 'group'
            else:
                if item['portal_type'] in view_action_types:
                    url = "%s/view" % url
                dpi = (
                    "target: #document-body; "
                    "source: #document-body; "
                    "history: record"
                )
                content_type = 'document'

            cls = 'item %s type-%s %s' % (content_type, typ, desc)

            items.append({
                'id': item['getId'],
                'cls': cls,
                'title': item['Title'],
                'description': item['Description'],
                'url': url,
                'type': utils.TYPE_MAP.get(item['portal_type'], 'none'),
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
        workspace = utils.parent_workspace(self.context)
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

    # Grouping code
    def set_show_extra_cookie(self):
        utils.set_show_extra_cookie(self.request, self.section)

    def set_grouping_cookie(self):
        grouping = self.request.get('grouping', 'label')
        member = api.user.get_current()
        cookie_name = '%s-group-by-%s' % (self.section, member.getId())
        utils.set_cookie(self.request, cookie_name, grouping)

    def set_sorting_cookie(self):
        sorting = self.request.get('sorting', 'modified')
        member = api.user.get_current()
        cookie_name = '%s-sort-on-%s' % (self.section, member.getId())
        utils.set_cookie(self.request, cookie_name, sorting)

    def get_from_request_or_cookie(self, key, cookie_name, default):
        if key in self.request:
            return self.request.get(key)
        if cookie_name in self.request:
            return self.request.get(cookie_name)
        return default

    @property
    def grouping(self):
        member = api.user.get_current()
        cookie_name = '%s-group-by-%s' % (self.section, member.getId())
        return self.get_from_request_or_cookie(
            "grouping", cookie_name, "label_custom")

    @property
    def sorting(self):
        member = api.user.get_current()
        cookie_name = '%s-sort-on-%s' % (self.section, member.getId())
        return self.get_from_request_or_cookie(
            "sorting", cookie_name, "modified")

    @property
    def show_extra(self):
        cookie_name = '%s-show-extra-%s' % (
            self.section, api.user.get_current().getId())
        return self.request.get(cookie_name, '').split('|')

    def group_headers(self):
        """ Return the headers (i.e. values) under a particular grouping
            (e.g. label, author, type).
        """
        # workspace can also be a contract, get_workspace_or_contract
        # handles both
        workspace = utils.get_workspace_or_contract(self.context)
        # if the user may not view the workspace, don't bother with
        # getting groups
        user = api.user.get_current()
        if not user.has_permission('View', workspace):
            return []
        grouping = self.grouping
        if grouping == 'period':
            headings = ['Today', 'Last Week', 'Last Month', 'All Time']
            return [dict(heading=x) for x in headings]
        try:
            storage = getAdapter(workspace, IGroupingStorage)
        except ComponentLookupError:
            # This happens if objects are loaded outside of an actual workspace
            # This is possible because we still have old content left which
            # star has not moved into workspaces yet - or cms
            # Examples: stardesk/projects-and-activities,
            # stardesk/boards-committees, stardesk/about-the-company
            # Changing logging to info, as no action is required from us
            log.info("Could not load GroupStorage for: %s"
                     % workspace.absolute_url())
            return []

        if grouping.endswith('_custom'):
            headers = storage.get_order_for(
                grouping.split('_')[0],
                include_archived='archived_tags' in self.show_extra,
            )
        else:
            headers = storage.get_order_for(
                grouping,
                include_archived='archived_tags' in self.show_extra,
                alphabetical=True
            )

        if grouping in ('label', 'label_custom'):
            headers.append(dict(heading='Untagged', archived=False))
        elif grouping == 'author':
            # If we are grouping by 'author', but the filter is for documents
            # only by the current user, then we return only the current user as
            # a grouping.
            if 'my_documents' in self.show_extra:
                username = user.getId()
                return [dict(heading=username)]
        elif grouping == 'type':
            # Return the human readable titles.
            vocab = queryUtility(IVocabularyFactory,
                                 name=config.DOCUMENT_TYPE)(self)
            headers = [
                dict(heading=vocab.getTermByToken(h['heading']).title,
                     value=vocab.getTermByToken(h['heading']).value)
                for h in headers]
            headers.append(dict(heading='Other', value='none'))
            return headers
        else:
            return [dict(heading='Ungrouped')]
        return headers
