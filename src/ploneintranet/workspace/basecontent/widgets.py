from datetime import datetime
from plone.app.event.base import default_timezone
from plone.app.event.dx.behaviors import IEventBasic
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
from zope.schema.interfaces import IDatetime


class IPatDatePickerWidget(IWidget):
    """ Marker interface """


@implementer_only(IPatDatePickerWidget)
class PatDatePickerWidget(Widget):
    """pat-date-picker gives us a list of strings with the date first and the
    time second. To extract the value we need to convert that to a datetime
    object.

    :rtype datetime:
    """
    def extract(self, default=NO_VALUE):
        value = self.request.get(self.name, default)
        if value == default:
            return default
        if isinstance(value, str):
            # Date only
            date = datetime(value, '%Y-%m-%d')
        if value[0] == u'':
            return None
        else:
            if value[1] == u'':
                value[1] = u'0:00'
            time_str = "{0} {1}".format(*value)
            date = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        date = date.replace(
            tzinfo=default_timezone(self.context, as_tzinfo=True))
        return date


class PatDatePickerConverter(BaseDataConverter):
    """toFieldValue just needs to return the datetime object
    """
    adapts(IDatetime, IPatDatePickerWidget)

    def toFieldValue(self, value):
        return value


@adapter(getSpecification(IEventBasic['start']), IWorkspaceAppFormLayer)
@implementer(IFieldWidget)
def StartPatDatePickerFieldWidget(field, request):
    return FieldWidget(field, PatDatePickerWidget(request))


@adapter(getSpecification(IEventBasic['end']), IWorkspaceAppFormLayer)
@implementer(IFieldWidget)
def EndPatDatePickerFieldWidget(field, request):
    return FieldWidget(field, PatDatePickerWidget(request))
