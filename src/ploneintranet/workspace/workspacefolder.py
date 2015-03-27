from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope import schema
from zope.event import notify
from zope.interface import implements

from ploneintranet.workspace.events import ParticipationPolicyChangedEvent
from ploneintranet.workspace import MessageFactory


class IWorkspaceFolder(form.Schema, IImageScaleTraversable):
    """
    Interface for WorkspaceFolder
    """
    calendar_visible = schema.Bool(
        title=MessageFactory(u"label_workspace_calendar_visibility",
                             u"Calendar visible in central calendar"),
        required=False,
        default=False,
    )
    email = schema.TextLine(
        title=MessageFactory(u'label_workspace_email', u'E-mail address'),
        required=False,
        default=u'',
    )


class WorkspaceFolder(Container):
    """
    A WorkspaceFolder users can collaborate in
    """
    implements(IWorkspaceFolder)

    # Block local role acquisition so that users
    # must be given explicit access to the workspace
    __ac_local_roles_block__ = 1

    def acquire_workspace(self):
        """
        helper method to acquire the workspace
        :rtype: ploneintranet.workspace.WorkspaceFolder
        """
        return self

    def can_manage_workspace(self):
        """
        does this user have permission to manage the workspace
        """
        return api.user.has_permission(
            "ploneintranet.workspace: Manage workspace",
            obj=self,
        )



    @property
    def external_visibility(self):
        return api.content.get_state(self)

    def set_external_visibility(self, value):
        api.content.transition(obj=self, to_state=value)

    @property
    def join_policy(self):
        try:
            return self._join_policy
        except AttributeError:
            return "admin"

    @join_policy.setter
    def join_policy(self, value):
        self._join_policy = value

    @property
    def participant_policy(self):
        try:
            return self._participant_policy
        except AttributeError:
            return "consumers"

    @participant_policy.setter
    def participant_policy(self, value):
        """ Changing participation policy fires a
        "ParticipationPolicyChanged" event
        """
        old_policy = self.participant_policy
        new_policy = value
        self._participant_policy = new_policy
        notify(ParticipationPolicyChangedEvent(self, old_policy, new_policy))

try:
    from ploneintranet.attachments.attachments import IAttachmentStoragable
except ImportError:
    IAttachmentStoragable = None

if IAttachmentStoragable is not None:
    from zope import interface
    interface.classImplements(WorkspaceFolder, IAttachmentStoragable)
