# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZPublisher.HTTPRequest import record

import logging


log = logging.getLogger(__name__)


class ChangemetadataView(BaseCartView):

    title = _('Change metadata')
    checked_permission = 'Modify portal content'

    allowed_record_keys = [
        'description',
        'subject',
        'title',
    ]

    def confirm(self):
        index = ViewPageTemplateFile("templates/changemetadata_confirmation.pt")  # noqa
        return index(self)

    def fix_record(self, record):
        '''
        We want the record to be a dict and
        the subject field of the record should be fixed
        to be a tuple in order to compare it properly with the object value
        '''
        data = {}
        for key in self.allowed_record_keys:
            if key in record:
                if key == 'subject':
                    if record['subject']:
                        data[key] = tuple(record['subject'].split(','))
                    else:
                        data[key] = ()
                else:
                    data[key] = record[key]
        return data

    @property
    @memoize
    def records(self):
        ''' Extract the records from the request
        '''
        form = self.request.form
        records = {
            key: self.fix_record(value) for key, value in form.items()
            if isinstance(value, record)
        }
        return records

    def handle_obj(self, obj, record):
        ''' Handle an object with the given record
        '''
        if not api.user.has_permission('Modify portal content', obj=obj):
            msg = _(
                u"changemetadata_permission_denied for",
                default=u"Cannot modify: ${title}",
                mapping={"title": obj.title}
            )
            api.portal.show_message(
                message=msg,
                request=self.request,
                type="error",
            )
            return

        good_keys = [key for key in self.allowed_record_keys if key in record]
        changed = 0
        for key in good_keys:
            obj_value = getattr(obj, key, u'')
            record_value = record[key]
            if obj_value != record_value:
                setattr(obj, key, record_value)
                changed += 1
        if changed:
            obj.reindexObject()
            self.update_groupings(obj)
        return changed

    def handle(self):
        ''' Check the request parameter, update the objects if needed,
        and return the list of the handled objects
        '''
        records = self.records
        if not records:
            return []
        uids = list(records.iterkeys())
        objs = (b.getObject() for b in api.content.find(UID=uids))
        handled = [
            obj.title
            for obj in objs
            if self.handle_obj(obj, records[obj.UID()])
        ]
        return handled

    def changemetadata(self):
        handled = self.handle()
        if handled:
            titles = ', '.join(sorted(handled))
            msg = _(
                u"batch_changemetadata_success",
                default=u"The following items have been updated: ${title_elems}",  # noqa
                mapping={"title_elems": titles}
            )
            api.portal.show_message(
                message=msg,
                request=self.request,
                type="success",
            )
        else:
            api.portal.show_message(
                message=_(u"No items could be updated"),
                request=self.request,
                type="info",
            )
        return self.redirect()
