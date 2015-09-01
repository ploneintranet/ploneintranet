from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile import field as namedfile
from plone.rfc822.interfaces import IPrimaryField
from plone.supermodel import model
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer


class IImageField(model.Schema):
    """We need to override the default image field so that we can interpret an
    empty string as NOT_CHANGED.
    """

    image = namedfile.NamedBlobImage(
        title=u'Image',
        description=u'',
        required=False,
    )

alsoProvides(IImageField, IFormFieldProvider)

# The equivalent of setting marshal:primary="true" on the field in the schema:
alsoProvides(IImageField['image'], IPrimaryField)


@implementer(IImageField)
@adapter(IDexterityContent)
class ImageField(object):

    def __init__(self, context):
        self.context = context
