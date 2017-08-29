# -*- coding: utf-8 -*-
from .utils import dexterity_update
from Acquisition import aq_inner
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from plone.app.event.base import default_timezone
from plone.memoize.view import memoize
from plone.rfc822.interfaces import IPrimaryFieldInfo
from ploneintranet import api as pi_api
from ploneintranet.calendar.utils import get_workspaces_of_current_user
from ploneintranet.calendar.utils import get_writable_workspaces_of_current_user  # noqa: E501
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.utils import get_record_from_registry
from ploneintranet.library.behaviors.publish import IPublishWidely
from ploneintranet.workspace.utils import map_content_type
from ploneintranet.workspace.utils import parent_app
from ploneintranet.workspace.utils import parent_workspace
from Products.CMFEditions.interfaces.IModifier import FileTooLargeToVersionError  # noqa
from Products.CMFEditions.utilities import isObjectChanged
from Products.CMFEditions.utilities import maybeSaveVersion
from Products.Five import BrowserView
from time import time
from urllib import urlencode
from zope.component import getUtility
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IVocabularyFactory


@implementer(IBlocksTransformEnabled)
class ContentView(BrowserView):
    """View and edit class/form for all default DX content-types."""

    _edit_permission = 'Modify portal content'

    _pat_redactor_options = [
        ('imageupload', '{workspace_url}/images-upload.json'),
        ('imagegetjson', '{workspace_url}/@@images.json'),
        ('imageresizable', 'true'),
        ('toolbar-external', '#editor-toolbar'),
        ('allowed-tags', (
            'p, ul, li, ol, strong, em, a, img, video, embed, object, '
            'h1, h2, h3, h4, h5, table, thead, tbody, th, tr, td, '
            'iframe, figure, figcaption'
        )),
        ('buttons', (
            'format, bold, italic, deleted, lists, link, horizontalrule, image'
        )),
        ('formatting', 'p, pre, h1, h2, h3'),
        ('plugins', 'bufferbuttons,alignment,table,source,video,imagemanager')
    ]

    @property
    @memoize
    def user(self):
        ''' The currently authenticated ploneintranet user profile (if any)
        '''
        return pi_api.userprofile.get_current()

    @property
    @memoize
    def form_data_pat_redactor(self):
        ''' Return the options for pat-redactor in the format:

        key1: value1; key2: value2; ...
        '''
        workspace = parent_workspace(self.context)
        options = '; '.join(
            ': '.join(option) for option in self._pat_redactor_options
        )
        return options.format(
            workspace_url=workspace.absolute_url()
        )

    @property
    @memoize
    def is_ajax(self):
        ''' Check if we have an ajax call
        '''
        requested_with = self.request.environ.get('HTTP_X_REQUESTED_WITH')
        return requested_with == 'XMLHttpRequest'

    @property
    @memoize
    def show_sidebar(self):
        ''' Should we show the sidebar?
        '''
        form = self.request.form
        if 'show_sidebar' in form:
            return True
        if 'hide_sidebar' in form:
            return False
        if self.is_ajax:
            return False
        return True

    def make_sidebar_items(self):
        ''' Make the equivalent of the sidebar items
        '''
        # First we pretend to mimic a sidebar result
        sidebar = api.content.get_view(
            'sidebar.documents',
            self.context,
            self.request,
        )
        pc = api.portal.get_tool(name='portal_catalog')
        brains = pc(UID=self.context.UID())
        results = sidebar._extract_attrs(brains)
        return map(sidebar.result2item, results)

    @property
    @memoize
    def include_clicktracker(self):
        """Is inclusion of slcclicktracker element enabled in the registry?"""
        include_slcclicktracker = get_record_from_registry(
            'ploneintranet.workspace.include_slcclicktracker',
            False)
        return include_slcclicktracker

    @property
    @memoize
    def autosave_enabled(self):
        ''' Look up the registry to check if autosave should be enabled
        for this portal_type
        '''
        autosave_portal_types = api.portal.get_registry_record(
            'ploneintranet.workspace.autosave_portal_types',
            default=[],
        )
        return self.context.portal_type in autosave_portal_types

    @property
    @memoize
    def autosave_delay(self):
        ''' The delay before triggering the autosave injection
        '''
        if self.autosave_enabled:
            return api.portal.get_registry_record(
                'ploneintranet.workspace.autosave_delay',
                default=2000,
            )

    @property
    @memoize
    def workspace(self):
        ''' Return the parent workspace (if there is any)
        '''
        return parent_workspace(self.context)

    def should_update(self):
        ''' Check if we should call the update method
        before rendering the template
        '''
        return self.request.method == 'POST'

    def __call__(self, title=None, description=None, tags=[], text=None):
        """Render the default template and evaluate the form when editing."""
        context = aq_inner(self.context)
        self.can_edit = api.user.has_permission(
            self._edit_permission,
            obj=context
        )
        # When saving, force to POST
        if self.should_update():
            self.update()

        return super(ContentView, self).__call__()

    def validate(self):
        ''' Return truish if valid
        '''
        return True

    @property
    @memoize
    def lock_info(self):
        ''' Return the lock information about this user
        '''
        view = api.content.get_view(
            'toggle-lock',
            self.context,
            self.request,
        )
        return view.lock_info

    @property
    @memoize
    def is_locked(self):
        ''' If the document is locked by another user do not update it
        '''
        info = self.lock_info
        if not info:
            return False
        user = self.user
        if not user or user.username == info.get('creator'):
            return False
        return True

    def get_lock_user_fullname(self):
        ''' Get the fullname of the user who has the lock
        '''
        info = self.lock_info or {}
        creator = info.get('creator')
        if not creator:
            return _('Anonymous User')
        user = pi_api.userprofile.get(creator)
        if not user:
            return creator
        return user.fullname or user.getId()

    @property
    @memoize
    def is_old_version(self):
        ''' Prevent overwriting changes by checking
        that the current object modification time is equal to the one
        known when the document form was rendered
        '''
        modified = self.request.form.get('dx_modified')
        if not modified:
            return False
        if isinstance(modified, list):
            modified = modified[0]
        if modified != self.context.dx_modified:
            return True
        self.request.form.pop('dx_modified')
        return False

    def update(self):
        """ """
        context = aq_inner(self.context)
        workflow_modified = False
        fields_modified = {}
        errors = []
        messages = []
        if self.is_locked:
            api.portal.show_message(
                _(
                    'document_locked_by_error',
                    'The document is locked by ${user}.',
                    mapping={
                        'user': self.get_lock_user_fullname(),
                    }
                ),
                self.request,
                'error',
            )
            return
        if self.is_old_version:
            msg = _(
                'document_modified_error',
                default=(
                    'It seems that this document was modified since '
                    'you loaded this form. '
                    'Your changes will be discarded. '
                    '<a href="${url}">'
                    'Please reload this page by clicking here</a>.'
                ),
                mapping={
                    'url': self.context.absolute_url(),
                }
            )
            api.portal.show_message(
                msg,
                self.request,
                'error',
            )
            return

        if (
                self.request.get('workflow_action') and
                not self.request.get('form.submitted')):
            api.content.transition(
                obj=context,
                transition=self.request.get('workflow_action')
            )
            # re-calculate can_edit after the workflow state change
            context.dx_modified = str(int(time()))
            self.can_edit = api.user.has_permission(
                self._edit_permission,
                obj=context
            )
            workflow_modified = True
            messages.append(
                context.translate(_("The workflow state has been changed.")))

        if self.can_edit:
            fields_modified = {}
            if self.validate():
                fields_modified, errors = dexterity_update(context)
                if fields_modified:
                    context.dx_modified = str(int(time()))
                    if not self.autosave_enabled:
                        messages.append(
                            _("Your changes have been saved.")
                        )

        versioning_errors = self.save_version()
        errors.extend(versioning_errors)

        if errors:
            error_msg = context.translate(_("There was a problem:"))
            api.portal.show_message(
                u"{} {}".format(error_msg, errors),
                request=self.request,
                type="error",
            )

        elif workflow_modified or fields_modified:
            if messages:
                api.portal.show_message(
                    ' '.join(messages), request=self.request,
                    type="success")

            if fields_modified:
                descriptions = [
                    Attributes(interface, *fields)
                    for interface, fields in fields_modified.items()]
                notify(ObjectModifiedEvent(context, *descriptions))
            else:
                context.reindexObject()

    def previews(self):
        return pi_api.previews.get_preview_urls(
            self.context,
            scale="large",
            with_timestamp=True,
        )

    def is_available(self):
        return pi_api.previews.has_previews(self.context)

    @memoize
    def is_allowed_document_type(self):
        return pi_api.previews.is_allowed_document_type(self.context)

    def converting(self):
        return pi_api.previews.converting(self.context)

    def successfully_converted(self):
        return pi_api.previews.successfully_converted(self.context)

    def image_url(self):
        """The img-url used to construct the img-tag."""
        context = aq_inner(self.context)
        if getattr(context, 'image', None) is not None:
            return '{}/@@images/image'.format(context.absolute_url())

    def icon_class(self):
        """Gets the icon class for the primary field of this content"""
        primary_field_info = IPrimaryFieldInfo(self.context)
        if hasattr(primary_field_info.value, "contentType"):
            contenttype = primary_field_info.value.contentType
            icon_name = map_content_type(contenttype)
            if icon_name:
                return 'icon-file-{0}'.format(icon_name)
        return 'icon-file-code'

    def content_type_name(self):
        """Gets a name for the type of the primary field of this content"""
        # Need this to be able to describe what is going to be downloaded
        # in the sharing tooltip. Cornelis seems to want to name the content
        # type in cleartext (Download as Microsoft Word) so we might will need
        # to extend this with a clear name mapper that then again might need
        # translation support. For now, return the name only.
        primary_field_info = IPrimaryFieldInfo(self.context)
        name = ''
        if hasattr(primary_field_info.value, "contentType"):
            contenttype = primary_field_info.value.contentType
            name = map_content_type(contenttype)
        if name:
            return name.capitalize()
        return "unknown"

    def delete_url(self):
        ''' Prepare a url to the delete form triggering:
         - pat-modal
         - pat-inject
        '''
        options = {
            'pat-modal': 'true',
            'pat-inject': ' && '.join([
                'source:#document-body; target:#document-body',
                'source:#workspace-events; target:#workspace-events',
                'source:#global-statusmessage; target:#global-statusmessage',
            ])
        }
        return "%s/delete_confirmation?%s#document-content" % (
            self.context.absolute_url(),
            urlencode(options)
        )

    @property
    def form_id(self):
        ''' The id to be used in the main form
        '''
        return self.context.UID()

    @property
    def sidebar_target(self):
        ''' When injecting the form we may want to reload some sidebar parts
        '''
        return 'item-{UID}'.format(
            UID=self.context.UID()
        )

    def form_pat_inject_options(self):
        ''' Return the data-path-inject options we want to use
        '''
        parts = [
            'source: #{mainid}; target: #{mainid};',
            'source: #{sidebar_target}-replacement; target: #{sidebar_target}; loading-class: \'\''  # noqa
        ]
        if self.autosave_enabled:
            mainid = 'saving-badge'
            parts.append('#workflow-menu; loading-class: \'\'')
        else:
            mainid = 'document-body'
        parts.append(
            'source:#global-statusmessage; target:#global-statusmessage; '
            'loading-class: \'\''
        )
        template = ' && '.join(parts)
        return template.format(
            mainid=mainid,
            sidebar_target=self.sidebar_target,
        )

    def get_preview_urls(self, obj):
        ''' Expose the homonymous pi_api method to get the list of preview_urls
        '''
        return pi_api.previews.get_preview_urls(obj)

    @property
    @memoize
    def friendly_type2type_class(self):
        ''' Reuse the method from the search view
        '''
        view = api.content.get_view(
            'proto',
            api.portal.get(),
            self.request,
        )
        return view.friendly_type2type_class

    def get_obj_icon_class(self, obj):
        ''' Return the best icon for this object
        '''
        if obj.portal_type == 'Image':
            return 'icon-file-image'
        if obj.portal_type == 'File' and obj.file:
            content_type = obj.file.contentType
            if content_type == 'message/rfc822':
                return 'icon-mail'
            for word in (
                'pdf',
                'word',
                'excel',
                'powerpoint',
                'video',
                'audio',
                'archive',
                'image',
            ):
                if word in content_type:
                    return 'icon-file-%s' % word
            return 'icon-attach'

        icon_type = self.friendly_type2type_class(obj.portal_type)
        icon_file = icon_type.replace('type', 'file')
        return 'icon-%s' % icon_file

    def portal_type_to_class(self):
        pt = self.context.portal_type
        if pt == 'File':
            return 'file'
        elif pt == 'Image':
            return 'image'
        elif pt == 'Link':
            return 'link'
        elif pt == 'Event':
            return 'event'
        elif pt == 'Document':
            return 'rich'
        elif pt == 'Folder':
            return 'folder'
        return 'generic'

    def save_version(self):
        errors = []
        comment = self.request.get('cmfeditions_version_comment', '')
        save_new_version = self.request.get('cmfeditions_save_new_version',
                                            None)
        force = save_new_version is not None

        if not (isObjectChanged(self.context) or force):
            return errors

        try:
            maybeSaveVersion(self.context, comment=comment, force=force)
        except FileTooLargeToVersionError as e:
            errors.append(e)
        return errors

    def is_versionable(self):
        portal_repository = api.portal.get_tool('portal_repository')
        return portal_repository.isVersionable(self.context)

    def can_publish_widely(self):
        try:
            return IPublishWidely(self.context).can_publish_widely()
        except TypeError:
            return False

    def copied_to_library_url(self):
        try:
            publish_adapter = IPublishWidely(self.context)
        except TypeError:
            return False
        target = publish_adapter.target()
        return target and target.absolute_url() or None


class ContainerView(ContentView):
    ''' For the container we always return the sidebar
    '''
    @property
    @memoize
    def show_sidebar(self):
        ''' Should we show the sidebar?
        '''
        form = self.request.form
        if 'show_sidebar' in form:
            return True
        if 'hide_sidebar' in form:
            return False
        return True


class HelperView(BrowserView):
    ''' Use this to provide helper methods
    '''

    def get_selected_tz(self):
        ''' Let's try to get this from the start attribute (if found).
        Otherwise default to the default timezone.
        '''
        try:
            return str(self.context.start.tzinfo)
        except:
            return default_timezone()

    def get_tz_options(self):
        '''Returns the timezone options to be used in a select
        '''
        selected_tz = self.get_selected_tz()
        plone_tzs = getUtility(
            IVocabularyFactory,
            'plone.app.vocabularies.CommonTimezones'
        )(self.context)
        # The offset and daylight depends on the date/time,
        # so it is not easy to set it up coherently
        return [{
            'id': x.token,
            'gmt_adjustment': '',  # "GMT+12:00",
            'use_daylight': '',  # 0
            'selected': x.token == selected_tz and x.token or None,
            'value': x.token,
            'label': x.title,  # '(GMT+12:00) Fiji, Kamchatka, Marshall Is.'
        } for x in plone_tzs]

    def get_user_workspaces(self):
        return get_workspaces_of_current_user(self.context)

    def get_writable_user_workspaces(self):
        return get_writable_workspaces_of_current_user(self.context)

    def safe_get_workspace(self):
        """ This will safely return a sane element, either a workspace, or
        app or portal object to call helper methods on
        """
        portal = api.portal.get()
        return parent_workspace(self.context) or \
            parent_app(self.context) or \
            portal

    def safe_member_prefill(self, context, name, default=''):
        """ Tries safely to get a members prefill and returns nothing otherwise
        without failing. This way a form can be used for add and edit and
        within and outside a workspace
        """
        workspace = self.safe_get_workspace()
        if hasattr(workspace, 'member_prefill'):
            return workspace.member_prefill(context, name, default)
        return default

    def safe_member_and_group_prefill(self, context, name, default=''):
        """ Tries safely to get a members prefill and returns nothing otherwise
        without failing. This way a form can be used for add and edit and
        within and outside a workspace
        """
        workspace = self.safe_get_workspace()
        if hasattr(workspace, 'member_and_group_prefill'):
            return workspace.member_and_group_prefill(context, name, default)
        return default
