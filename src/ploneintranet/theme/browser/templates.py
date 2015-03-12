from ploneintranet.theme.interfaces import IPloneIntranetFormLayer
from ploneintranet.theme import browser
import os.path
import plone.z3cform

path = lambda p: os.path.join(os.path.dirname(browser.__file__), 'templates', p)

layout_factory = plone.z3cform.templates.ZopeTwoFormTemplateFactory(
    path('layout.pt'),
    form=plone.z3cform.interfaces.IFormWrapper,
    request=IPloneIntranetFormLayer)
