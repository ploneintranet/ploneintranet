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


alsoProvides(ISimpleSharing, form.IFormFieldProvider)


class SimpleSharing(object):

    implements(ISimpleSharing)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context