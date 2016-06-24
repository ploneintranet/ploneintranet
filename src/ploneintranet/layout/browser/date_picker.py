# coding=utf-8
from json import dumps
from plone.memoize.view import memoize_contextless
from Products.Five.browser import BrowserView
from zope.i18nmessageid import MessageFactory


pl_message = MessageFactory('plonelocales')
pae_message = MessageFactory('plone.app.event')


class I18nJSONView(BrowserView):
    '''
    I am the date-picker-i18n.json view class

    Use me like this:
        <input class="pat-date-picker"
               ...
               data-pat-date-picker="...; i18n: ${portal_url}/@@date-picker-i18n.json; ..."  # noqa
               />
    '''

    @memoize_contextless
    def __call__(self):
        translate = self.context.translate
        json = dumps({
            "previousMonth": translate(pae_message("prev_month_link")),
            "nextMonth": translate(pae_message("next_month_link")),
            "months": [
                translate(pl_message(month)) for month in [
                    "month_jan",
                    "month_feb",
                    "month_mar",
                    "month_apr",
                    "month_may",
                    "month_jun",
                    "month_jul",
                    "month_aug",
                    "month_sep",
                    "month_oct",
                    "month_nov",
                    "month_dec",
                ]
            ],
            "weekdays": [
                translate(pl_message(weekday)) for weekday in [
                    "weekday_sun",
                    "weekday_mon",
                    "weekday_tue",
                    "weekday_wed",
                    "weekday_thu",
                    "weekday_fri",
                    "weekday_sat",
                ]
            ],
            "weekdaysShort": [
                translate(pl_message(weekday_abbr)) for weekday_abbr in [
                    "weekday_sun_abbr",
                    "weekday_mon_abbr",
                    "weekday_tue_abbr",
                    "weekday_wed_abbr",
                    "weekday_thu_abbr",
                    "weekday_fri_abbr",
                    "weekday_sat_abbr",
                ]
            ],
        })
        return json
