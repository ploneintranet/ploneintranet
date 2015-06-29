from plone.app.dexterity.behaviors.metadata import IDublinCore
from ploneintranet.workspace.interfaces import IWorkspaceAppFormLayer
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from z3c.form.interfaces import NO_VALUE
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.component import adapts
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import ITuple


class ICommaSeparatedWidget(IWidget):
    """ Marker interface """


@implementer_only(ICommaSeparatedWidget)
class CommaSeparatedWidget(Widget):
    def extract(self, default=NO_VALUE):
        """pat-autosuggest fields use a comma separated string as the value.
        Split that into a tuple of strings.

        :rtype tuple of strings: """
        value = self.request.get(self.name, default)
        if value == default:
            return default
        if isinstance(value, basestring):
            values = value.split(',')
            return tuple(values)


class CommaSeparatedConverter(BaseDataConverter):
    adapts(ITuple, ICommaSeparatedWidget)

    def toFieldValue(self, value):
        """Return the tuple of strings

        :rtype tuple of strings:
        """
        if value is None:
            return self.field.missing_value
        return value


@adapter(getSpecification(IDublinCore['subjects']), IWorkspaceAppFormLayer)
@implementer(IFieldWidget)
def CommaSeparatedFieldWidget(field, request):
    return FieldWidget(field, CommaSeparatedWidget(request))
