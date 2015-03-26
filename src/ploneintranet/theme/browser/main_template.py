from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.browser.main_template import MainTemplate


class PIMainTemplate(MainTemplate):
    main_template = ViewPageTemplateFile('templates/main_template.pt')
