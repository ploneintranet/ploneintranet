# coding=utf-8
from AccessControl import ClassSecurityInfo
from collective import dexteritytextindexer
from plone import api as plone_api
from plone.dexterity.content import Container
from plone.directives import form
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.membrane.interfaces import IGroup
from Products.membrane.interfaces import IMembraneGroupProperties
from Products.PlonePAS.sheet import MutablePropertySheet
from z3c.form import validator
from zope import schema
from zope.interface import implementer
from zope.interface import Invalid


class IWorkGroup(IGroup, IMembraneGroupProperties, form.Schema):

    """The core group schema.

    Most of the plone intranet UI relies on these fields.
    """

    dexteritytextindexer.searchable('id')
    id = schema.TextLine(
        title=_(u"ID"),
        required=True,
        missing_value=u'',
    )
    canonical = schema.TextLine(
        title=_(u"Canonical Group ID (may contain spaces)"),
        required=False,
        default=u'',
        missing_value=u'',
    )
    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u"Title"),
        required=False,
        default=u'',
        missing_value=u'',
    )
    dexteritytextindexer.searchable('description')
    description = schema.TextLine(
        title=_(u"Description"),
        required=False,
        default=u'',
        missing_value=u'',
    )
    dexteritytextindexer.searchable('mail')
    mail = schema.TextLine(
        title=_(u"Email"),
        required=False,
        default=u'',
        missing_value=u'',
    )
    members = schema.List(
        value_type=schema.ASCIILine(
            title=_(u'label_member_id', u'ID of a member'),
            required=True,
            default=''),
        title=_(u"Members"),
        required=False,
        default=[],
        missing_value=[],
    )


@implementer(IWorkGroup)
class WorkGroup(Container):

    """Work Group content type."""

    def Title(self):
        """
        return the title
        """
        return self.title

    def Description(self):
        """
        return the description
        """
        return self.description

    def Email(self):
        """
        return the email
        """
        return self.mail

    def getGroupId(self):
        """
        return the group id
        """
        return self.canonical or self.id

    def getGroupName(self):
        return self.context.title

    def getGroupMembers(self):
        """
        return the members of the given group
        """
        # XXX filter for really existing members
        return self.members

    workspace_members = getGroupMembers

    def getRoles(self):
        """
        return the roles that group members should gain
        """
        return []

    def getPropertiesForUser(self, user, request=None):
        '''Get properties for this group.
        '''
        properties = {
            'id': self.canonical,
            'title': self.title.encode('utf8'),
            'description': (self.description or u'').encode('utf8'),
            'email': (self.mail or u'').encode('utf8'),
            'canonical': self.canonical.encode('utf8'),
            'object_id': self.id,
        }
        return MutablePropertySheet(**properties)


class WorkGroupIdValidator(validator.SimpleFieldValidator):

    """Two users can't have the same username."""

    def validate(self, value, force=False):
        membrane_tool = plone_api.portal.get_tool('membrane_tool')
        groupids = membrane_tool._catalog.uniqueValuesFor('exact_getGroupId')
        if value in groupids:
            brains = membrane_tool.searchResults(exact_getGroupId=value)
            if brains and self.context != brains[0].getObject():
                raise Invalid(_("A group with this id already exists"))

        return super(WorkGroupIdValidator, self).validate(value)


validator.WidgetValidatorDiscriminators(
    WorkGroupIdValidator,
    field=IWorkGroup['id'])


class WorkGroupGroupsProvider(object):
    """
    Determine the groups to which a principal belongs.
    A principal can be a user or a group.

    See the docstring of
    ploneintranet.workspace.behaviors.groups.MembraneWorkspaceGroupsProvider
    for in depth information on the call flow.

    """

    security = ClassSecurityInfo()

    def __init__(self, context):
        self.context = context

    def _iterGroups(self, userid=None):
        catalog = plone_api.portal.get_tool('portal_catalog')
        query = {'object_provides': IWorkGroup}
        if userid:
            query['workspace_members'] = userid
        return (b.id for b in catalog.unrestrictedSearchResults(query))

    # IGroupsPlugin implementation
    def getGroupsForPrincipal(self, principal, request=None):
        groups = set()
        for group in self._iterGroups(principal.getId()):
            groups.add(group)
        return tuple(groups)
    security.declarePrivate('getGroupsForPrincipal')
