from plone.directives import form
from rwproperty import getproperty, setproperty
from zope.interface import implements, alsoProvides, Interface
from zope.component import adapts
from zope.schema import Bool

from ploneintranet.readstatus import MessageFactory as _

class IMustRead(form.Schema):
    """MustRead schema
    """

    form.fieldset(
            'categorization',
            label=_(u'Categorization'),
            fields=('mustread',),
        )

    mustread = Bool(
            title=u"Must read",
            description=u"""Mark the content as "Must read" for all users.""",
            default=False,
            required=False,
        )

alsoProvides(IMustRead, form.IFormFieldProvider)

class IMustReadMarker(Interface):
    """Marker interface that will be provided by instances using the
    IMustRead behavior.
    """