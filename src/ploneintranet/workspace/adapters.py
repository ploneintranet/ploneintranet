from Products.CMFCore.interfaces import IContentish
from borg.localrole.default_adapter import DefaultLocalRoleAdapter
from borg.localrole.interfaces import ILocalRoleProvider
from collective.workspace.interfaces import IHasWorkspace
from collective.workspace.workspace import Workspace
from plone import api
from zope.interface import implements
from zope.component import adapts
from Acquisition import aq_inner
from Acquisition import Implicit
from BTrees.OOBTree import OOBTree
from datetime import datetime
from plone.folder.ordered import OrderedBTreeFolderBase
from plone.uuid.interfaces import IUUID
from OFS.owner import Owned
import persistent
from plone.dexterity.interfaces import IDexterityContent


class PloneIntranetWorkspace(Workspace):
    """
    A custom workspace behaviour, based on collective.workspace

    Here we define our own available groups, and the roles
    they are given on the workspace.
    """

    # A list of groups to which team members can be assigned.
    # Maps group name -> roles
    available_groups = {
        u'Admins': ('Contributor', 'Editor', 'Reviewer',
                    'Reader', 'TeamManager',),
        u'Members': ('TeamMember', ),
        # These are the 'participation policy' groups
        u'Consumers': (),
        u'Producers': ('Contributor',),
        u'Publishers': ('Contributor', 'SelfPublisher',),
        u'Moderators': ('Reader', 'Contributor', 'Reviewer', 'Editor',),
    }

    def add_to_team(self, **kw):
        """
        We override this method to add our additional participation
        policy groups, as detailed in available_groups above
        """
        group = self.context.participant_policy.title()
        data = kw.copy()
        if "groups" in data:
            data["groups"].add(group)
        else:
            data["groups"] = set([group])

        super(PloneIntranetWorkspace, self).add_to_team(**data)

    def group_for_policy(self, policy=None):
        """
        Lookup the collective.workspace usergroup corresponding to the
        given policy

        :param policy: The value of the policy to lookup, defaults to the
                       current policy
        :type policy: str
        """
        if policy is None:
            policy = self.context.participant_policy
        return "%s:%s" % (policy.title(), self.context.UID())


class WorkspaceLocalRoleAdapter(DefaultLocalRoleAdapter):
    """
    If the user has the local role of Owner on the context
    and the acquired role of SelfPublisher; they should also be given Reviewer.

    """
    implements(ILocalRoleProvider)
    adapts(IContentish)

    def getRoles(self, principal_id):
        """
        give an Owner who is also a 'selfpublisher', the reviewer role
        """
        context = self.context
        current_roles = list(DefaultLocalRoleAdapter.getRoles(
            self,
            principal_id,
        ))

        # check we are not on the workspace itself
        if IHasWorkspace.providedBy(context):
            return current_roles
        # otherwise we should acquire the workspace and check out roles
        workspace = getattr(context, 'acquire_workspace', lambda: None)()
        if workspace is None:
            return current_roles

        workspace_roles = api.user.get_roles(obj=workspace)
        if 'SelfPublisher' in workspace_roles and 'Owner' in current_roles:
            current_roles.append('Reviewer')
        return current_roles


class GroupingStorageValues(
        Implicit, Owned, persistent.Persistent):
    """ A datastructure to store the UIDs of objects appearing under a specific
        grouping.

        It conforms to the requirements imposed by OrderedBTreeFolderBase on
        its sub-objects (acquisition aware, ownable, persistent).
    """

    def __init__(self, uids):
        self.archived = False
        self.uids = set(uids)

    def __iter__(self):
        return self.uids.__iter__()

    def __contains__(self, item):
        return item in self.uids

    def __len__(self):
        return len(self.uids)

    def add(self, item):
        self.uids.add(item)

    def discard(self, item):
        self.uids.discard(item)

    def remove(self, item):
        self.uids.remove(item)

    def pop(self):
        return self.uids.pop()


class GroupingStorage(object):
    """ Adapter that stores the sidebar's groupings for quick lookup.

        The groupings dict is arranged in the following way:
        OOBTree({
            'label': {
                'Important': set([uid, uid, uid]),
                'Frivolous': set([uid, uid]),
            }
            'author: {
                'max-mustermann': set([uid]),
                'john-doe': set([uid, uid]),
                'jane-doe': set([uid]),
            }
            'type': {
                'foo': set([uid]),
                'bar': set([uid, uid, uid]),
                'baz': set([uid]),
            }
        })
        The top-level keys are the groupings.

        For each grouping we store another dict.

        Each key in this dict is a unique value for that grouping. These values
        are retrieved from the objects stored in the workspace.

        For each key we have a list of uids. These are the uids of the objects
        that have that key as a field value (corresponding to the grouping).

        Remember: each grouping is a field on an object, so each value of that
        grouping is a value of that field on an object inside the workspace.

        We need to keep track of the uids, so that we know when to remove a
        grouping-value. When an object is modified, we don't know if anything
        was removed (for example from the 'Subject' field, which corresponds to
        'label' grouping).

        So we have to check every time if that object's uid is in any grouping
        values that that object doesn't have anymore. In that way, we know to
        remove the uid from that grouping-value. If that grouping-value doesn't
        have any uids anymore, we can remove it.
    """

    def __init__(self, context):
        self.context = context
        context = aq_inner(self.context)
        if not hasattr(context, '_groupings'):
            self.init_groupings()

    def clear_groupings(self):
        self.init_groupings()

    def init_groupings(self):
        context = aq_inner(self.context)
        context._groupings = OOBTree({
            'label': OrderedBTreeFolderBase(),
            'author': OrderedBTreeFolderBase(),
            'type': OrderedBTreeFolderBase(),
        })

    def _add_grouping_values(self, grouping, values, obj):
        """ Add $uid to the list of uids stored under the grouping values
            (provided by $values) in the groupings datastructure.

            If the list doesn't exist yet, add it.
        """
        uid = IUUID(obj)
        groupings = self.get_groupings()
        for value in values:
            if value in groupings[grouping]:
                if uid in groupings[grouping][value]:
                    continue
                else:
                    groupings[grouping][value].add(uid)
                    groupings[grouping][value]._p_changed = 1
            else:
                groupings[grouping][value] = GroupingStorageValues([uid])

        groupings[grouping]._p_changed = 1
        groupings._p_changed = 1

    def _remove_grouping_values(self, grouping, values, obj):
        """ Remove $uid from the list of uids stored under the grouping values
            (provided by $values) in the groupings datastructure.

            If $uid is the only one in the list, then remove the
            list (and its key) entirely.
        """
        uid = IUUID(obj)
        groupings = self.get_groupings()
        for value in groupings[grouping].keys():
            if value not in values and uid in groupings[grouping][value]:
                if len(groupings[grouping][value]) == 1:
                    del groupings[grouping][value]
                else:
                    groupings[grouping][value].discard(uid)
                    groupings[grouping][value]._p_changed = 1

            groupings[grouping]._p_changed = 1

        groupings._p_changed = 1

    def _remove_grouping_value(self, grouping, value):
        """ Remove entry $value under a given $grouping.

            Can be used for bulk-changes to a grouping (e.g. changing a tag)
        """
        groupings = self.get_groupings()
        if value in groupings[grouping]:
            del groupings[grouping][value]

    def get_groupings(self):
        context = aq_inner(self.context)
        return context._groupings

    def update_groupings(self, obj):
        """ Update the groupings dict with the values stored on obj.
        """
        context = aq_inner(self.context)
        groupings = context._groupings
        # label
        self._remove_grouping_values('label', obj.Subject(), obj)
        self._add_grouping_values('label', obj.Subject(), obj)

        # handle documentType
        if IDexterityContent.providedBy(obj):
            field = obj.Schema().getField('documentType')
            if field:
                types = field.get(obj)
                self._remove_grouping_values('type', types, obj)
                self._add_grouping_values('type', types, obj)

        # author
        self._add_grouping_values('author', [obj.Creator()], obj)
        self._remove_grouping_values('author', [obj.Creator()], obj)

        context._groupings = groupings
        context._groupings_modified = datetime.now()
        context._p_changed = 1

    def reset_order(self):
        """ Reset the order for all groupings to default, i.e. same order
            as the keys of the OOBTree
        """
        groupings = self.get_groupings()
        for grouping in groupings.keys():
            self.set_order_for(
                grouping,
                sorted([k for k in groupings[grouping].keys()])
            )

    def get_order_for(self,
                      grouping,
                      include_archived=False,
                      alphabetical=False):
        """ """
        groupings = self.get_groupings()
        grouping_obj = groupings.get(grouping)
        if not grouping_obj:
            return []
        if alphabetical:
            order = sorted(grouping_obj.keys())
        else:
            order = grouping_obj.getOrdering().idsInOrder()
        if include_archived:
            return [
                dict(heading=g, archived=grouping_obj.get(g).archived) for
                g in order]
            return order
        return [
            dict(heading=g, archived=False) for g in order if not
            grouping_obj.get(g).archived]

    def set_order_for(self, grouping, order):
        """ Set order for a given grouping"""
        grouping = self.get_groupings()[grouping]
        for uid in order:
            grouping.moveObjectToPosition(
                uid, order.index(uid), suppress_events=True)

    def remove_from_groupings(self, obj):
        """ Remove obj's grouping relevant information to its workspace.
        """
        self._remove_grouping_values('type', [], obj)
        self._remove_grouping_values('label', [], obj)
        self._remove_grouping_values('author', [], obj)
        context = aq_inner(self.context)
        groupings = context._groupings
        context._groupings = groupings
        context._groupings_modified = datetime.now()
        # context._p_changed = 1

    def modified(self):
        """ Return the last time this grouping storage was modified.
        """
        context = aq_inner(self.context)
        if hasattr(context, '_groupings_modified'):
            if type(context._groupings_modified) == datetime:
                return context._groupings_modified
        return datetime.min
