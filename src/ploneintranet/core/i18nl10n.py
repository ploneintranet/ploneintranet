# -*- coding: utf-8 -*-
from Acquisition import aq_acquire
from DateTime import DateTime
from DateTime.interfaces import IDateTime
from Products.CMFPlone.i18nl10n import _interp_regex
from Products.CMFPlone.i18nl10n import datetime_formatvariables
from Products.CMFPlone.i18nl10n import name_formatvariables
from Products.CMFPlone.i18nl10n import get_formatstring_from_registry
from Products.CMFPlone.i18nl10n import weekdayname_msgid
from Products.CMFPlone.i18nl10n import weekdayname_msgid_abbr
from Products.CMFPlone.i18nl10n import monthname_msgid
from Products.CMFPlone.i18nl10n import monthname_msgid_abbr
from Products.CMFPlone.utils import log
from zope.i18n import translate
import logging


def ulocalized_time(
        time,
        long_format=None,
        time_only=False,
        context=None,
        domain='plonelocales',
        formatstring_domain='plonelocales',
        request=None,
        target_language=None):
    """Unicode aware localized time method (l10n), extended from CMFPlone
        The ONLY change versus CMFPlone is the extra parameter
        `formatstring_domain`.
        This allows us to define a different date_format_long in ploneintranet,
        while still being able to use the default translations provided by
        plonelocales, e.g. for the month names.
    """

    if time_only:
        msgid = 'time_format'
    elif long_format:
        msgid = 'date_format_long'
    else:
        msgid = 'date_format_short'

    # NOTE: this requires the presence of three msgids inside the translation
    #       catalog date_format_long, date_format_short, and time_format
    #       These msgids are translated using interpolation.
    #       The variables used here are the same as used in the strftime
    #       formating.
    #       Supported are:
    #           %A, %a, %B, %b, %H, %I, %m, %d, %M, %p, %S, %Y, %y, %Z
    #       Each used as variable in the msgstr without the %.
    #       For example: "${A} ${d}. ${B} ${Y}, ${H}:${M} ${Z}"
    #       Each language dependend part is translated itself as well.

    # From http://docs.python.org/lib/module-time.html
    #
    # %a    Locale's abbreviated weekday name.
    # %A        Locale's full weekday name.
    # %b        Locale's abbreviated month name.
    # %B        Locale's full month name.
    # %d        Day of the month as a decimal number [01,31].
    # %H        Hour (24-hour clock) as a decimal number [00,23].
    # %I        Hour (12-hour clock) as a decimal number [01,12].
    # %m        Month as a decimal number [01,12].
    # %M        Minute as a decimal number [00,59].
    # %p        Locale's equivalent of either AM or PM.
    # %S        Second as a decimal number [00,61].
    # %y        Year without century as a decimal number [00,99].
    # %Y        Year with century as a decimal number.
    # %Z        Time zone name (no characters if no time zone exists).

    mapping = {}
    # convert to DateTime instances. Either a date string or
    # a DateTime instance needs to be passed.
    if not IDateTime.providedBy(time):
        try:
            time = DateTime(time)
        except:
            log('Failed to convert %s to a DateTime object' % time,
                severity=logging.DEBUG)
            return None

    if context is None:
        # when without context, we cannot do very much.
        return time.ISO8601()

    if request is None:
        request = aq_acquire(context, 'REQUEST')

    # 1. if our Enabled flag in the configuration registry is set,
    # the format string there should override the translation machinery
    formatstring = get_formatstring_from_registry(msgid)
    if formatstring is not None:
        return time.strftime(formatstring)

    # 2. the normal case: translation machinery,
    # that is the ".../LC_MESSAGES/plonelocales.po" files
    # XXX: here, we pass `formatstring_domain` instead of `domain`
    formatstring = translate(msgid, formatstring_domain, mapping, request,
                             target_language=target_language)

    # 3. if both failed, fall back to hardcoded ISO style
    if formatstring == msgid:
        if msgid == 'date_format_long':
            formatstring = '%Y-%m-%d %H:%M'  # 2038-01-19 03:14
        elif msgid == 'date_format_short':
            formatstring = '%Y-%m-%d'  # 2038-01-19
        elif msgid == 'time_format':
            formatstring = '%H:%M'  # 03:14
        else:
            formatstring = '[INTERNAL ERROR]'
        return time.strftime(formatstring)

    # get the format elements used in the formatstring
    formatelements = _interp_regex.findall(formatstring)

    # reformat the ${foo} to foo
    formatelements = [el[2:-1] for el in formatelements]

    # add used elements to mapping
    elements = [e for e in formatelements if e in datetime_formatvariables]

    # add weekday name, abbr. weekday name, month name, abbr month name
    week_included = True
    month_included = True

    name_elements = [e for e in formatelements if e in name_formatvariables]
    if not ('a' in name_elements or 'A' in name_elements):
        week_included = False
    if not ('b' in name_elements or 'B' in name_elements):
        month_included = False

    for key in elements:
        mapping[key] = time.strftime('%' + key)

    if week_included:
        weekday = int(time.strftime('%w'))  # weekday, sunday = 0
        if 'a' in name_elements:
            mapping['a'] = weekdayname_msgid_abbr(weekday)
        if 'A' in name_elements:
            mapping['A'] = weekdayname_msgid(weekday)
    if month_included:
        monthday = int(time.strftime('%m'))  # month, january = 1
        if 'b' in name_elements:
            mapping['b'] = monthname_msgid_abbr(monthday)
        if 'B' in name_elements:
            mapping['B'] = monthname_msgid(monthday)

    # translate translateable elements
    # Note: Here, the normal `domain` is used
    for key in name_elements:
        mapping[key] = translate(mapping[key], domain,
                                 context=request, default=mapping[key],
                                 target_language=target_language)

    # translate the time string
    # XXX: here, we pass `formatstring_domain` instead of `domain`
    return translate(msgid, formatstring_domain, mapping, request,
                     target_language=target_language)
