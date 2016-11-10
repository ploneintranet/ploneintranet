from .policies import PARTICIPANT_POLICY
from collective.workspace.interfaces import IWorkspace
from json import dumps
from plone import api
from plone.dexterity.content import Container
from ploneintranet import api as pi_api
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.events import ParticipationPolicyChangedEvent
from ploneintranet.workspace.interfaces import IWorkspaceFolder
from zope.event import notify
from zope.interface import implementer


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
        it for custom styling.

        Keep in sync with registry record
        ploneintranet.workspace.workspace_types_css_mapping
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

    def existing_users(self):
        """
        Look up the full user details for current workspace members

        BBB: this has to go away. The workspace view has more performant
             methods
        """
        members = IWorkspace(self).members
        gtool = self.portal_groups
        group_names = gtool.listGroupNames()
        info = []
        portal_url = api.portal.get().absolute_url()

        for user_or_group_id, details in members.items():
            user = api.user.get(user_or_group_id)
            if user is not None:
                typ = 'user'
                user = user.getUser()
                title = (user.getProperty('fullname') or user.getId() or
                         user_or_group_id)
                # XXX tbd, we don't know what a persons description is, yet
                description = ''
                classes = 'user ' + (description and 'has-description' or
                                     'has-no-description')
                portrait = pi_api.userprofile.avatar_url(user_or_group_id)
                obj = user
                absolute_url = '/'.join(
                    (portal_url, 'profiles', user.getId())
                )
            else:
                typ = 'group'
                group = api.group.get(user_or_group_id)
                if group is None:
                    continue
                # Don't show a secret group, ever
                if group.getProperty('state') == 'secret':
                    continue
                title = (group.getProperty('title') or group.getGroupId() or
                         user_or_group_id)
                # Resolving all users of a group with nested groups is
                # ridiculously slow. PAS resolves each member and if it
                # doesn't return a valid user, it resolves it as group
                # and from that group every member again. With LDAP,
                # Each of these is one ldap request. 'Hammering' is not
                # the right word for this.
                # At this position, it is not vital to return this information
                # Instead we can simply say how many members/groups there are.
                # People can click and see for themselves.
                group_members = gtool.getGroupMembers(group.getId())
                groups = 0
                for member in group_members:
                    if member in group_names:
                        groups += 1
                description = _(
                    u"number_of_members",
                    default=u'${no_users} Users / ${no_groups} Groups',
                    mapping={
                        u'no_users': len(group_members) - groups,
                        u'no_groups': groups})
                classes = 'user-group has-description'
                portrait = ''
                obj = group
                obj.getProperty('object_id') or obj.getId()

                absolute_url = '/'.join((
                    portal_url,
                    'groups',
                    obj.getProperty('object_id') or obj.getId()
                ))

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
                    typ=typ,
                    obj=obj,
                    absolute_url=absolute_url,
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
        field_value = getattr(context, field, default)
        if not field_value:
            return ''
        assigned_users = field_value.split(',')
        prefill = {}
        for user_id in assigned_users:
            user = api.user.get(user_id)
            if user:
                prefill[user_id] = (
                    user.getProperty('fullname') or
                    user.getId() or user_id
                )
        if prefill:
            return dumps(prefill)
        else:
            return ''

    def member_and_group_prefill(self, context, field, default=None):
        """
        Return JSON for pre-filling a pat-autosubmit field with the values for
        that field
        """
        acl_users = api.portal.get_tool('acl_users')
        field_value = getattr(context, field, default)
        if not field_value:
            return ''
        assigned_users = field_value.split(',')
        prefill = {}
        for assignee_id in assigned_users:
            user = api.user.get(assignee_id)
            if user:
                prefill[assignee_id] = (
                    user.getProperty('fullname') or
                    user.getId() or assignee_id
                )
            else:
                group = acl_users.getGroupById(assignee_id)
                if group:
                    prefill[assignee_id] = (
                        group.getProperty('title') or
                        group.getId() or assignee_id
                    )
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
