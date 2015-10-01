from collections import defaultdict
from collective.workspace.interfaces import IWorkspace
from json import dumps
from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.todo.behaviors import ITodo
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.events import ParticipationPolicyChangedEvent
from ploneintranet import api as pi_api
from zope import schema
from zope.event import notify
from zope.interface import implementer
from .policies import PARTICIPANT_POLICY


class IWorkspaceFolder(form.Schema, IImageScaleTraversable):
    """
    Interface for WorkspaceFolder
    """
    calendar_visible = schema.Bool(
        title=_(
            u"label_workspace_calendar_visibility",
            u"Calendar visible in central calendar"),
        required=False,
        default=False,
    )
    email = schema.TextLine(
        title=_(u'label_workspace_email', u'E-mail address'),
        required=False,
        default=u'',
    )


@implementer(IWorkspaceFolder, IAttachmentStoragable)
class WorkspaceFolder(Container):
    """
    A WorkspaceFolder users can collaborate in
    """

    # Block local role acquisition so that users
    # must be given explicit access to the workspace
    __ac_local_roles_block__ = 1

    def acquire_workspace(self):
        """
        helper method to acquire the workspace
        :rtype: ploneintranet.workspace.WorkspaceFolder
        """
        return self

    @property
    def external_visibility(self):
        return api.content.get_state(self)

    def set_external_visibility(self, value):
        api.content.transition(obj=self, to_state=value)

    @property
    def is_case(self):
        """ XXX remove after case refactoring """
        return False

    @property
    def ws_type(self):
        """
        returns a string for use in a css selector in the templates
        describing this content type
        Override in custom workspace types, if you want to make use of
        it for custom styling
        """
        return "workspace"

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
        IWorkspace(self).update_participant_policy_groups(
            old_policy,
            new_policy,
        )
        notify(ParticipationPolicyChangedEvent(self, old_policy, new_policy))

    def tasks(self):
        items = defaultdict(list) if self.is_case else []
        catalog = api.portal.get_tool('portal_catalog')
        wft = api.portal.get_tool('portal_workflow')
        current_path = '/'.join(self.getPhysicalPath())
        ptype = 'todo'
        brains = catalog(
            path=current_path,
            portal_type=ptype,
            sort_on='due')
        for brain in brains:
            obj = brain.getObject()
            todo = ITodo(obj)
            assignee = api.user.get(obj.assignee) if obj.assignee else None
            initiator = api.user.get(obj.initiator) if obj.initiator else None
            data = {
                'id': brain.UID,
                'title': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'checked': wft.getInfoFor(todo, 'review_state') == u'done',
                'due': obj.due,
                'assignee': assignee,
                'initiator': initiator,
            }
            if self.is_case:
                milestone = "unassigned"
                if obj.milestone not in ["", None]:
                    milestone = obj.milestone
                items[milestone].append(data)
            else:
                items.append(data)
        if self.is_case:
            for milestone in items.keys():
                # Show the checked tasks before the unchecked tasks
                items[milestone].sort(key=lambda x: x['checked'] is False)
        return items

    def existing_users(self):
        """
        Look up the full user details for current workspace members
        """
        members = IWorkspace(self).members
        info = []

        for user_or_group_id, details in members.items():
            user = api.user.get(user_or_group_id)
            if user is not None:
                typ = 'user'
                user = user.getUser()
                title = (user.getProperty('fullname') or user.getId() or
                         user_or_group_id)
                # XXX tbd, we don't know what a persons description is, yet
                description = ''
                classes = 'user ' + (description and 'has-description'
                                     or 'has-no-description')
                portrait = pi_api.userprofile.avatar_url(user_or_group_id)
            else:
                typ = 'group'
                group = api.group.get(user_or_group_id)
                if group is None:
                    continue
                title = (group.getProperty('title') or group.getId() or
                         user_or_group_id)
                description = _(
                    u"number_of_members",
                    default=u'${no_members} Members',
                    mapping={
                        u'no_members': len(group.getAllGroupMemberIds())})
                classes = 'user-group has-description'
                portrait = ''

            # User's 'role' is any group they are a member of
            # that is not the default participation policy group
            # (including Admins group)
            role = None
            groups = details['groups']
            if 'Admins' in groups:
                role = 'Admin'
            for policy in PARTICIPANT_POLICY:
                if policy == self.participant_policy:
                    continue
                if policy.title() in groups:
                    role = PARTICIPANT_POLICY[policy]['title']
                    # According to the design there is at most one extra role
                    # per user, so we go with the first one we find. This may
                    # not be enforced in the backend though.
                    break
            if role:
                classes += ' has-label'

            info.append(
                dict(
                    id=user_or_group_id,
                    title=title,
                    description=description,
                    portrait=portrait,
                    cls=classes,
                    member=True,
                    admin='Admins' in details['groups'],
                    role=role,
                    typ=typ
                )
            )

        return info

    def existing_users_by_id(self):
        """
        A dict version of existing_users userid for the keys, to simplify
        looking up details for a user by id
        """
        users = self.existing_users()
        users_by_id = {}
        for user in users:
            users_by_id[user['id']] = user
        return users_by_id

    def member_prefill(self, context, field, default=None):
        """
        Return JSON for pre-filling a pat-autosubmit field with the values for
        that field
        """
        users = self.existing_users()
        field_value = getattr(context, field, default)
        prefill = {}
        if field_value:
            assigned_users = field_value.split(',')
            for user in users:
                if user['id'] in assigned_users:
                    prefill[user['id']] = user['title']
        if prefill:
            return dumps(prefill)
        else:
            return ''


class IWorkflowWorkspaceFolder(IWorkspaceFolder):
    """
    Interface for WorkflowWorkspaceFolder
    """


@implementer(IWorkflowWorkspaceFolder, IAttachmentStoragable)
class WorkflowWorkspaceFolder(Container):
    """
    A WorkspaceFolder with Workflow users can collaborate in
    """
