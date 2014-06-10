from collective.workspace.vocabs import UsersSource
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from zope.component import adapts
from zope.interface import alsoProvides, implements
from zope import schema


class ISimpleSharing(form.Schema):

    visibility = schema.Choice(
        title=u"Visibility",
        description=u"Who should see this document?",
        vocabulary='ploneintranet.simplesharing.workflow_states_vocab',
    )

    share_with = schema.Choice(
        title=u"Share with",
        description=u"The users with whom you'd like to share this content",
        source=UsersSource,
    )


alsoProvides(ISimpleSharing, form.IFormFieldProvider)


class SimpleSharing(object):

    implements(ISimpleSharing)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context
