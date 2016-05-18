# coding=utf-8
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.interfaces import IPloneintranetFormLayer
from z3c.form.browser.select import SelectWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import ISelectWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import IChoice


@implementer_only(ISelectWidget)
class PloneIntranetSelectWidget(SelectWidget):
    '''Select widget implementation.
    '''
    noValueMessage = _('Unknown')


@adapter(IChoice, Interface, IPloneintranetFormLayer)
@implementer(IFieldWidget)
def PloneIntranetSelectFieldWidget(field, source, request=None):
    '''Not much more than a brutal copy/paste of the SelectFieldWidget.
    '''
    if request is None:
        real_request = source
    else:
        real_request = request
    return FieldWidget(field, PloneIntranetSelectWidget(real_request))
