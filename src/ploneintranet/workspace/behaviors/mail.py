# -*- coding: utf-8 -*-
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from plone.app.textfield import RichText as RichTextField
from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives as form
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from zope.schema import TextLine
from zope.schema import Tuple
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.app.textfield.value import RichTextValue


@provider(IFormFieldProvider)
class IMail(model.Schema):

    mail_from = TextLine(
        title=_('from', u'From'),
        description=u'',
        default=u'',
    )

    mail_to = Tuple(
        title=_('to', u'To'),
        description=u'',
        value_type=TextLine(),
        default=(),
        required=False,
    )

    mail_cc = Tuple(
        title=_('cc', u'CC'),
        description=u'',
        value_type=TextLine(),
        default=(),
        required=False,
    )

    mail_bcc = Tuple(
        title=_('bcc', u'BCC'),
        description=u'',
        value_type=TextLine(),
        missing_value=(),
        required=False,
    )

    mail_body = RichTextField(
        title=_('body', u'Body'),
        description=u"",
        required=False,
        default=RichTextValue(u''),
    )
    form.widget('mail_body', RichTextFieldWidget)
    model.primary('mail_body')


@implementer(IMail)
@adapter(IDexterityContent)
class Mail(object):

    def __init__(self, context):
        self.context = context
