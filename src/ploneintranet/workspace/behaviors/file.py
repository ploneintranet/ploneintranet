from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile import field as namedfile
from plone.rfc822.interfaces import IPrimaryField
from plone.supermodel import model
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer


class IFileField(model.Schema):
    """We need to override the default file field so that we can interpret an
    empty string as NOT_CHANGED.
    """

    file = namedfile.NamedBlobFile(
        title=u'File',
        description=u'',
        required=False,
    )

alsoProvides(IFileField, IFormFieldProvider)

# The equivalent of setting marshal:primary="true" on the field in the schema:
alsoProvides(IFileField['file'], IPrimaryField)


@implementer(IFileField)
@adapter(IDexterityContent)
class FileField(object):

    def __init__(self, context):
        self.context = context
