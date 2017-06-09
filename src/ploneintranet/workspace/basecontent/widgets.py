# coding=utf-8
from datetime import datetime
from plone.app.event.base import default_timezone
from plone.app.event.dx.behaviors import IEventBasic
from plone.formwidget.namedfile.converter import NamedDataConverter
from plone.namedfile.interfaces import INamedField
from ploneintranet.layout.interfaces import IPloneintranetFormLayer
from ploneintranet.network.behaviors.metadata import IDublinCore as pi_IDublinCore  # noqa
from ploneintranet.workspace.behaviors.event import IPloneIntranetEvent
from ploneintranet.workspace.behaviors.file import IFileField
from ploneintranet.workspace.behaviors.image import IImageField
from ploneintranet.workspace.interfaces import IBaseWorkspaceFolder
from ploneintranet.workspace.interfaces import IWorkspaceAppFormLayer
from pytz import timezone
from z3c.form.converter import BaseDataConverter
from z3c.form.converter import DateDataConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IWidget
from z3c.form.interfaces import NO_VALUE
from z3c.form.interfaces import NOT_CHANGED
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.component import adapts
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import ISequence


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
            self.request.get('%s-timezone' % self.name, '') or
            self.request.get('timezone', '') or
            default_timezone(self.context)
        )
        if isinstance(timezone_name, unicode):
            timezone_name.encode('utf8')

        # pytz "does not work" with datetime tzinfo. Use localize instead
        # Symptoms are times in "LMT" format which are off a few minutes.
        # http://stackoverflow.com/questions/24856643/unexpected-results-converting-timezones-in-python  # noqa
        tz = timezone(timezone_name)
        date = tz.localize(date)
        return date


@implementer_only(IPatDatePickerWidget)
class DateCheckboxWidget(Widget):
    """Stores the date when a checkbox was checked

    :rtype datetime:
    """

    def extract(self, default=NO_VALUE):
        value = self.request.get(self.name, default)
        if (
            value == default or
            not value or
            not isinstance(value, basestring)
        ):
            return None

        date = datetime.strptime(value, '%Y-%m-%d')

        timezone_name = default_timezone(self.context)
        if isinstance(timezone_name, unicode):
            timezone_name.encode('utf8')

        # pytz "does not work" with datetime tzinfo. Use localize instead
        # Symptoms are times in "LMT" format which are off a few minutes.
        # http://stackoverflow.com/questions/24856643/unexpected-results-converting-timezones-in-python  # noqa
        tz = timezone(timezone_name)
        date = tz.localize(date)
        return date

    def render(self):
        pass


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


@adapter(getSpecification(IEventBasic['start']), IPloneintranetFormLayer)
@implementer(IFieldWidget)
def StartPatDatePickerFieldWidget(field, request):
    return FieldWidget(field, PatDatePickerWidget(request))


@adapter(getSpecification(IEventBasic['end']), IPloneintranetFormLayer)
@implementer(IFieldWidget)
def EndPatDatePickerFieldWidget(field, request):
    return FieldWidget(field, PatDatePickerWidget(request))


@adapter(
    getSpecification(IBaseWorkspaceFolder['archival_date']),
    IWorkspaceAppFormLayer
)
@implementer(IFieldWidget)
def ArchivalDatePickerFieldWidget(field, request):
    return FieldWidget(field, DateCheckboxWidget(request))


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


class ISortableListWidget(IWidget):
    ''' Marker interface '''


@implementer_only(ISortableListWidget)
class SortableListWidget(Widget):
    ''' A widget for a list of sortable elements, as represented with
        pat-sortable on the front-end.
    '''

    def extract(self, default=NO_VALUE):
        value = self.request.get(self.name, default)
        if value == default:
            return value
        if not isinstance(value, (tuple, list)):
            value = [value]
        return filter(None, value)


@adapter(
    getSpecification(IPloneIntranetEvent['agenda_items']),
    IWorkspaceAppFormLayer,
)
@implementer(IFieldWidget)
def SortableListFieldWidget(field, request):
    return FieldWidget(field, SortableListWidget(request))


@adapter(ISequence, ISortableListWidget)
class SortableListConverter(BaseDataConverter):
    """ Data converter for ISortableListWidget.
    """

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        collectionType = self.field._type
        if isinstance(collectionType, tuple):
            collectionType = collectionType[-1]
        return collectionType(value)
