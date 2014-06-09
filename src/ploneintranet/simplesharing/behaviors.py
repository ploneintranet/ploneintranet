from plone.directives import form
from zope.interface import alsoProvides
from zope import schema


class ISimpleSharing(form.Schema):

    visibility = schema.Choice(
        title=u"Visibility",
        description=u"Who should see this document?",
        vocabulary=workflow_states,
    )


alsoProvides(ISimpleSharing, form.IFormFieldProvider)
