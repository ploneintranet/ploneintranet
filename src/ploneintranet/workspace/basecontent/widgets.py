from datetime import datetime
from plone.app.event.base import default_timezone
from plone.app.event.dx.behaviors import IEventBasic
from plone.formwidget.namedfile.converter import NamedDataConverter
from plone.namedfile.interfaces import INamedField
from ploneintranet.workspace.behaviors.image import IImageField
from ploneintranet.workspace.behaviors.file import IFileField
from ploneintranet.workspace.interfaces import IWorkspaceAppFormLayer
from pytz import timezone
from z3c.form.converter import BaseDataConverter
from z3c.form.converter import DateDataConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from z3c.form.interfaces import NOT_CHANGED
from z3c.form.interfaces import NO_VALUE
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.component import adapts
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import ITuple

from ploneintranet.network.behaviors.metadata import IDublinCore \
    as pi_IDublinCore


class ICommaSeparatedWidget(IWidget):
    """ Marker interface """


@implementer_only(ICommaSeparatedWidget)
class CommaSeparatedWidget(Widget):
    def extract(self, default=NO_VALUE):
        """pat-autosuggest fields use a comma separated string as the value.
        Split that into a tuple of strings.

        :rtype tuple of strings: """
        value = self.request.get(self.name, default)
        if value == u'':
            return ()
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


# plone intranet uses a dublincore override
@adapter(getSpecification(pi_IDublinCore['subjects']), IWorkspaceAppFormLayer)
@implementer(IFieldWidget)
def CommaSeparatedFieldWidget(field, request):
    return FieldWidget(field, CommaSeparatedWidget(request))


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
        timezone_name = (
            self.request.get('%s-timezone' % self.name, '')
            or self.request.get('timezone', '')
            or default_timezone(self.context)
        )
        if isinstance(timezone_name, unicode):
            timezone_name.encode('utf8')
        date = date.replace(tzinfo=timezone(timezone_name))
        return date


class PatDatePickerConverter(BaseDataConverter):
    """toFieldValue just needs to return the datetime object
    """
    adapts(IDatetime, IPatDatePickerWidget)

    def toFieldValue(self, value):
        return value


@implementer(IDataConverter)
class PatDatePickerDataConverter(DateDataConverter):
    """A special data converter for dates."""
    adapts(IDate, IPatDatePickerWidget)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if isinstance(value, datetime):
            return value
        return super(PatDatePickerDataConverter).toFieldValue(value)


@adapter(getSpecification(IEventBasic['start']), IWorkspaceAppFormLayer)
@implementer(IFieldWidget)
def StartPatDatePickerFieldWidget(field, request):
    return FieldWidget(field, PatDatePickerWidget(request))


@adapter(getSpecification(IEventBasic['end']), IWorkspaceAppFormLayer)
@implementer(IFieldWidget)
def EndPatDatePickerFieldWidget(field, request):
    return FieldWidget(field, PatDatePickerWidget(request))


class IPloneIntranetFileWidget(IWidget):
    """ Marker interface """


@implementer_only(IPloneIntranetFileWidget)
class PloneIntranetFileWidget(Widget):
    def extract(self, default=NOT_CHANGED):
        """Return NOT_CHANGED if a filename isn't specified.

        The user should the Image object if they want to delete the image.
        """
        value = self.request.get(self.name, default)
        if value == u'':
            return default
        else:
            return value


class PloneIntranetFileConverter(NamedDataConverter):
    adapts(INamedField, IPloneIntranetFileWidget)


@adapter(getSpecification(IImageField['image']), IWorkspaceAppFormLayer)
@implementer(IFieldWidget)
def PloneIntranetImageFieldWidget(field, request):
    return FieldWidget(field, PloneIntranetFileWidget(request))


@adapter(getSpecification(IFileField['file']), IWorkspaceAppFormLayer)
@implementer(IFieldWidget)
def PloneIntranetFileFieldWidget(field, request):
    return FieldWidget(field, PloneIntranetFileWidget(request))
