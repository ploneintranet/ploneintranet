# coding=utf-8
from plone.app.contenttypes.interfaces import IEvent
from plone.autoform.interfaces import IFormFieldProvider
from zope import schema
from zope.interface import alsoProvides


class IPloneIntranetEvent(IEvent):
    """Additional fields for PloneIntranet events
    """
    agenda_items = schema.List(
        title=u"Agenda Items",
        description=u"Items associated with this event",
        required=False,
        default=[],
    )

    organizer = schema.TextLine(
        title=u'Organizer',
        description=u'The user id of the event organizer',
        required=False,
    )

    invitees = schema.TextLine(
        title=u'Invitees',
        description=u'Members who are invited to the event',
        required=False,
    )

alsoProvides(IPloneIntranetEvent, IFormFieldProvider)
